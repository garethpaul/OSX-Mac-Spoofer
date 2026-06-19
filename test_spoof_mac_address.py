import argparse
import importlib.util
import io
import pathlib
import unittest
from contextlib import redirect_stdout
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "spoof_mac_address", str(ROOT / "SpoofMACAddress.py")
)
spoof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(spoof)


class SpoofMacAddressTest(unittest.TestCase):
    def test_normalize_mac_address_accepts_compact_and_colon_forms(self):
        self.assertEqual(
            "02:23:45:67:89:ab",
            spoof.normalize_mac_address("0223456789AB"),
        )
        self.assertEqual(
            "02:23:45:67:89:ab",
            spoof.normalize_mac_address("02:23:45:67:89:AB"),
        )

    def test_normalize_observed_mac_address_accepts_hardware_addresses(self):
        self.assertEqual(
            "00:23:45:67:89:ab",
            spoof.normalize_observed_mac_address("00:23:45:67:89:AB"),
        )

    def test_normalize_mac_address_rejects_bad_values(self):
        for value in [
            "",
            "01:23:45",
            "zz:23:45:67:89:ab",
            "02:23:45:67:89:ab;whoami",
            "00:00:00:00:00:00",
            "01:23:45:67:89:ab",
            "00:23:45:67:89:ab",
        ]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    spoof.normalize_mac_address(value)

    def test_normalize_mac_address_rejects_non_string_values(self):
        for value in [None, 123, b"0223456789ab"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    spoof.normalize_mac_address(value)

    def test_validate_interface_rejects_shell_metacharacters(self):
        self.assertEqual("en0", spoof.validate_interface(" en0 "))
        for value in [
            "",
            "-a",
            "--help",
            "en0;reboot",
            "en0 $(id)",
            "en0/../../tmp",
        ]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    spoof.validate_interface(value)

    def test_validate_interface_rejects_non_string_values(self):
        for value in [None, 123, b"en0"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    spoof.validate_interface(value)

    def test_parse_mac_address_extracts_and_normalizes(self):
        self.assertEqual(
            "00:bb:cc:dd:ee:ff",
            spoof.parse_mac_address("ether 00:BB:CC:DD:EE:FF"),
        )

    def test_parse_mac_address_rejects_non_string_output(self):
        for value in [None, 123, b"ether 00:BB:CC:DD:EE:FF"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    spoof.parse_mac_address(value)

    def test_execute_rejects_malformed_commands(self):
        for command in [
            [],
            (),
            "ifconfig en0",
            b"ifconfig en0",
            [""],
            ["ifconfig", " "],
            ["ifconfig", None],
        ]:
            with self.subTest(command=command):
                with self.assertRaises(ValueError):
                    spoof.execute(command, dry_run=True)

    def test_execute_dry_run_omits_command_arguments(self):
        output = io.StringIO()
        with redirect_stdout(output):
            spoof.execute(
                ["ifconfig", "private-interface", "ether", "02:23:45:67:89:ab"],
                dry_run=True,
            )

        self.assertEqual("+ ifconfig\n", output.getvalue())
        for sensitive_value in ["private-interface", "02:23:45:67:89:ab", "ether"]:
            self.assertNotIn(sensitive_value, output.getvalue())

        output = io.StringIO()
        with redirect_stdout(output):
            spoof.execute(["private-command", "host-secret"], dry_run=True)
        self.assertEqual("+ command\n", output.getvalue())

    def test_execute_uses_bounded_timeout(self):
        completed = mock.Mock(returncode=0, stdout="ok", stderr="")
        with mock.patch.object(spoof.subprocess, "run", return_value=completed) as run:
            self.assertEqual("ok", spoof.execute(["ifconfig", "en0"]))

        self.assertEqual(spoof.COMMAND_TIMEOUT_SECONDS, run.call_args.kwargs["timeout"])

    def test_execute_reports_timeout_without_command_arguments(self):
        timeout = spoof.subprocess.TimeoutExpired(
            cmd=["/sbin/ifconfig", "private-interface"],
            timeout=spoof.COMMAND_TIMEOUT_SECONDS,
        )
        with mock.patch.object(spoof.subprocess, "run", side_effect=timeout):
            with self.assertRaises(RuntimeError) as raised:
                spoof.execute(["/sbin/ifconfig", "private-interface"])

        self.assertEqual("ifconfig timed out after 15 seconds", str(raised.exception))
        self.assertNotIn("private-interface", str(raised.exception))
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    def test_execute_reports_failure_without_output_or_command_arguments(self):
        completed = mock.Mock(
            returncode=23,
            stdout="private-interface 02:23:45:67:89:ab",
            stderr="host-secret diagnostic",
        )
        with mock.patch.object(spoof.subprocess, "run", return_value=completed):
            with self.assertRaises(RuntimeError) as raised:
                spoof.execute(["/sbin/ifconfig", "private-interface"])

        message = str(raised.exception)
        self.assertEqual("ifconfig failed with exit status 23", message)
        for sensitive_value in [
            "private-interface",
            "02:23:45:67:89:ab",
            "host-secret",
            "diagnostic",
        ]:
            self.assertNotIn(sensitive_value, message)
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    def test_execute_reports_launch_failure_without_os_details_or_arguments(self):
        failure = FileNotFoundError(
            2, "No such file or directory", "/private/path/ifconfig"
        )
        with mock.patch.object(spoof.subprocess, "run", side_effect=failure):
            with self.assertRaises(RuntimeError) as raised:
                spoof.execute(["/sbin/ifconfig", "private-interface"])

        message = str(raised.exception)
        self.assertEqual("ifconfig could not be started", message)
        for sensitive_value in [
            "private-interface",
            "/private/path",
            "No such file",
            "Errno",
        ]:
            self.assertNotIn(sensitive_value, message)
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    def test_change_commands_are_argument_lists(self):
        commands = spoof.change_commands(
            "en0",
            "0223456789ab",
            airport_interface="en1",
        )

        self.assertIn(
            ["/sbin/ifconfig", "en0", "ether", "02:23:45:67:89:ab"],
            commands,
        )
        self.assertEqual("/usr/sbin/networksetup", commands[0][0])
        self.assertEqual(spoof.PATH_TO_AIRPORT, commands[1][0])
        self.assertEqual("/usr/sbin/networksetup", commands[3][0])
        for command in commands:
            self.assertIsInstance(command, list)
            self.assertTrue(pathlib.PurePosixPath(command[0]).is_absolute())

    def test_get_mac_address_uses_absolute_system_paths(self):
        with mock.patch.object(
            spoof,
            "execute",
            side_effect=[
                "ether 00:23:45:67:89:ab",
                "Ethernet Address: 00:11:22:33:44:55",
            ],
        ) as execute:
            self.assertEqual("00:23:45:67:89:ab", spoof.get_mac_address("en0"))
            self.assertEqual(
                "00:11:22:33:44:55",
                spoof.get_mac_address("en0", hardware=True),
            )

        self.assertEqual(
            [
                mock.call(["/sbin/ifconfig", "en0"]),
                mock.call(["/usr/sbin/networksetup", "-getmacaddress", "en0"]),
            ],
            execute.call_args_list,
        )

    def test_set_mac_address_dry_run_does_not_read_current_address(self):
        output = io.StringIO()
        with mock.patch.object(spoof, "get_mac_address") as get_mac_address:
            with redirect_stdout(output):
                spoof.set_mac_address("en0", "0223456789ab", dry_run=True)

        get_mac_address.assert_not_called()
        self.assertEqual(
            [
                "Dry run: no network state will be changed.",
                "+ networksetup",
                "+ airport",
                "+ ifconfig",
                "+ networksetup",
            ],
            output.getvalue().splitlines(),
        )
        for sensitive_value in ["en0", "en1", "02:23:45:67:89:ab", "ether"]:
            self.assertNotIn(sensitive_value, output.getvalue())

    def test_set_mac_address_rejects_post_change_mismatch_without_identifiers(self):
        with mock.patch.object(spoof, "execute") as execute:
            with mock.patch.object(
                spoof,
                "get_mac_address",
                side_effect=[
                    "00:23:45:67:89:ab",
                    "00:11:22:33:44:55",
                    "02:aa:bb:cc:dd:ee",
                ],
            ) as get_mac_address:
                with self.assertRaisesRegex(
                    RuntimeError,
                    "interface address did not match requested value after mutation",
                ) as raised:
                    spoof.set_mac_address("en0", "02:23:45:67:89:ab")

        self.assertEqual(4, execute.call_count)
        self.assertEqual(
            [
                mock.call("en0"),
                mock.call("en0", hardware=True),
                mock.call("en0"),
            ],
            get_mac_address.call_args_list,
        )
        message = str(raised.exception)
        self.assertNotIn("en0", message)
        self.assertNotIn("02:23:45:67:89:ab", message)
        self.assertNotIn("02:aa:bb:cc:dd:ee", message)
        self.assertIn("inspect and restore state manually", message)
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    def test_set_mac_address_captures_hardware_before_mutation(self):
        events = []
        observed_addresses = iter(
            ["00:23:45:67:89:ab", "00:11:22:33:44:55", "02:23:45:67:89:ab"]
        )

        def get_mac_address(interface, *, hardware=False):
            events.append("hardware" if hardware else "current")
            return next(observed_addresses)

        def execute(command):
            events.append("execute")

        output = io.StringIO()
        with mock.patch.object(spoof, "get_mac_address", side_effect=get_mac_address):
            with mock.patch.object(spoof, "execute", side_effect=execute):
                with redirect_stdout(output):
                    spoof.set_mac_address("en0", "02:23:45:67:89:ab")

        self.assertEqual(
            ["current", "hardware", "execute", "execute", "execute", "execute", "current"],
            events,
        )
        self.assertEqual(
            "Interface address change verified.\n"
            "Inspect and restore the interface manually if connectivity is unexpected.\n",
            output.getvalue(),
        )
        for sensitive_value in [
            "en0",
            "00:23:45:67:89:ab",
            "00:11:22:33:44:55",
            "02:23:45:67:89:ab",
        ]:
            self.assertNotIn(sensitive_value, output.getvalue())

    def test_set_mac_address_hardware_lookup_failure_prevents_mutation(self):
        with mock.patch.object(spoof, "execute") as execute:
            with mock.patch.object(
                spoof,
                "get_mac_address",
                side_effect=[
                    "00:23:45:67:89:ab",
                    RuntimeError("networksetup failed with exit status 1"),
                ],
            ):
                with self.assertRaisesRegex(RuntimeError, "networksetup failed"):
                    spoof.set_mac_address("en0", "02:23:45:67:89:ab")

        execute.assert_not_called()

    def test_set_mac_address_preserves_failure_before_address_mutation(self):
        failure = RuntimeError("networksetup failed with exit status 7")
        with mock.patch.object(spoof, "execute", side_effect=failure) as execute:
            with mock.patch.object(
                spoof,
                "get_mac_address",
                side_effect=["00:23:45:67:89:ab", "00:11:22:33:44:55"],
            ) as get_mac_address:
                with self.assertRaisesRegex(RuntimeError, str(failure)) as raised:
                    spoof.set_mac_address("en0", "02:23:45:67:89:ab")

        self.assertIs(failure, raised.exception)
        self.assertEqual(1, execute.call_count)
        self.assertEqual(2, get_mac_address.call_count)

    def test_set_mac_address_reports_partial_state_after_address_mutation(self):
        failure = RuntimeError("networksetup failed for en0 with secret output")
        with mock.patch.object(
            spoof,
            "execute",
            side_effect=[None, None, None, failure],
        ) as execute:
            with mock.patch.object(
                spoof,
                "get_mac_address",
                side_effect=["00:23:45:67:89:ab", "00:11:22:33:44:55"],
            ) as get_mac_address:
                with self.assertRaisesRegex(
                    RuntimeError,
                    "network command failed after interface address mutation",
                ) as raised:
                    spoof.set_mac_address("en0", "02:23:45:67:89:ab")

        self.assertEqual(4, execute.call_count)
        self.assertEqual(2, get_mac_address.call_count)
        message = str(raised.exception)
        for sensitive_value in [
            "en0",
            "02:23:45:67:89:ab",
            "secret output",
            "exit status",
        ]:
            self.assertNotIn(sensitive_value, message)
        self.assertIn("inspect and restore state manually", message)
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    def test_set_mac_address_reports_partial_state_when_mutation_command_fails(self):
        failure = RuntimeError("ifconfig failed for en0 with secret output")
        with mock.patch.object(
            spoof,
            "execute",
            side_effect=[None, None, failure],
        ) as execute:
            with mock.patch.object(
                spoof,
                "get_mac_address",
                side_effect=["00:23:45:67:89:ab", "00:11:22:33:44:55"],
            ) as get_mac_address:
                with self.assertRaisesRegex(
                    RuntimeError,
                    "network command failed after interface address mutation",
                ) as raised:
                    spoof.set_mac_address("en0", "02:23:45:67:89:ab")

        self.assertEqual(3, execute.call_count)
        self.assertEqual(2, get_mac_address.call_count)
        message = str(raised.exception)
        for sensitive_value in [
            "en0",
            "02:23:45:67:89:ab",
            "secret output",
            "exit status",
        ]:
            self.assertNotIn(sensitive_value, message)
        self.assertIn("inspect and restore state manually", message)
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    def test_set_mac_address_reports_partial_state_when_mutation_cannot_start(self):
        failure = RuntimeError("ifconfig could not be started")
        with mock.patch.object(
            spoof,
            "execute",
            side_effect=[None, None, failure],
        ) as execute:
            with mock.patch.object(
                spoof,
                "get_mac_address",
                side_effect=["00:23:45:67:89:ab", "00:11:22:33:44:55"],
            ) as get_mac_address:
                with self.assertRaisesRegex(
                    RuntimeError,
                    "network command failed after interface address mutation",
                ) as raised:
                    spoof.set_mac_address("en0", "02:23:45:67:89:ab")

        self.assertEqual(3, execute.call_count)
        self.assertEqual(2, get_mac_address.call_count)
        message = str(raised.exception)
        for sensitive_value in ["en0", "02:23:45:67:89:ab", "ifconfig"]:
            self.assertNotIn(sensitive_value, message)
        self.assertIn("inspect and restore state manually", message)
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    def test_set_mac_address_reports_partial_state_when_verification_lookup_fails(self):
        failure = RuntimeError("ifconfig failed for en0 with secret output")
        with mock.patch.object(
            spoof,
            "execute",
            side_effect=[None, None, None, None],
        ) as execute:
            with mock.patch.object(
                spoof,
                "get_mac_address",
                side_effect=[
                    "00:23:45:67:89:ab",
                    "00:11:22:33:44:55",
                    failure,
                ],
            ) as get_mac_address:
                with self.assertRaisesRegex(
                    RuntimeError,
                    "network command failed after interface address mutation",
                ) as raised:
                    spoof.set_mac_address("en0", "02:23:45:67:89:ab")

        self.assertEqual(4, execute.call_count)
        self.assertEqual(3, get_mac_address.call_count)
        message = str(raised.exception)
        for sensitive_value in [
            "en0",
            "02:23:45:67:89:ab",
            "secret output",
            "exit status",
        ]:
            self.assertNotIn(sensitive_value, message)
        self.assertIn("inspect and restore state manually", message)
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    def test_set_mac_address_reports_partial_state_when_verification_output_is_invalid(self):
        with mock.patch.object(
            spoof,
            "execute",
            side_effect=[None, None, None, None],
        ) as execute:
            with mock.patch.object(
                spoof,
                "get_mac_address",
                side_effect=[
                    "00:23:45:67:89:ab",
                    "00:11:22:33:44:55",
                    ValueError("no MAC address found for en0 in secret output"),
                ],
            ) as get_mac_address:
                with self.assertRaisesRegex(
                    RuntimeError,
                    "network command failed after interface address mutation",
                ) as raised:
                    spoof.set_mac_address("en0", "02:23:45:67:89:ab")

        self.assertEqual(4, execute.call_count)
        self.assertEqual(3, get_mac_address.call_count)
        message = str(raised.exception)
        for sensitive_value in ["en0", "02:23:45:67:89:ab", "secret output"]:
            self.assertNotIn(sensitive_value, message)
        self.assertIn("inspect and restore state manually", message)
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    def test_resolve_target_defaults_and_manual_values(self):
        args = argparse.Namespace(
            interface=None,
            address=None,
            airport_interface="en1",
        )
        output = io.StringIO()
        with redirect_stdout(output):
            target = spoof.resolve_target(args)
        self.assertEqual(("en0", spoof.DEFAULT_WIRED_ADDRESS, "en1"), target)

        args = argparse.Namespace(
            interface="en2",
            address="aabbccddeeff",
            airport_interface="en0",
        )
        output = io.StringIO()
        with redirect_stdout(output):
            target = spoof.resolve_target(args)
        self.assertEqual(("en2", "aabbccddeeff", "en0"), target)


if __name__ == "__main__":
    unittest.main()
