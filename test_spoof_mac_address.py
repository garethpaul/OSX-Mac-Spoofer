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

    def test_execute_uses_bounded_timeout(self):
        completed = mock.Mock(returncode=0, stdout="ok", stderr="")
        with mock.patch.object(spoof.subprocess, "run", return_value=completed) as run:
            self.assertEqual("ok", spoof.execute(["ifconfig", "en0"]))

        self.assertEqual(spoof.COMMAND_TIMEOUT_SECONDS, run.call_args.kwargs["timeout"])

    def test_execute_reports_timeout_without_command_arguments(self):
        timeout = spoof.subprocess.TimeoutExpired(
            cmd=["ifconfig", "private-interface"],
            timeout=spoof.COMMAND_TIMEOUT_SECONDS,
        )
        with mock.patch.object(spoof.subprocess, "run", side_effect=timeout):
            with self.assertRaisesRegex(RuntimeError, "ifconfig timed out after 15 seconds") as raised:
                spoof.execute(["ifconfig", "private-interface"])

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
            with self.assertRaisesRegex(
                RuntimeError, "ifconfig failed with exit status 23"
            ) as raised:
                spoof.execute(["ifconfig", "private-interface"])

        message = str(raised.exception)
        for sensitive_value in [
            "private-interface",
            "02:23:45:67:89:ab",
            "host-secret",
            "diagnostic",
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

        self.assertIn(["ifconfig", "en0", "ether", "02:23:45:67:89:ab"], commands)
        for command in commands:
            self.assertIsInstance(command, list)

    def test_set_mac_address_dry_run_does_not_read_current_address(self):
        output = io.StringIO()
        with mock.patch.object(spoof, "get_mac_address") as get_mac_address:
            with redirect_stdout(output):
                spoof.set_mac_address("en0", "0223456789ab", dry_run=True)

        get_mac_address.assert_not_called()
        self.assertIn("Dry run", output.getvalue())
        self.assertIn("ifconfig en0 ether 02:23:45:67:89:ab", output.getvalue())

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
