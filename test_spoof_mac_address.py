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
            "01:23:45:67:89:ab",
            spoof.normalize_mac_address("0123456789AB"),
        )
        self.assertEqual(
            "01:23:45:67:89:ab",
            spoof.normalize_mac_address("01:23:45:67:89:AB"),
        )

    def test_normalize_mac_address_rejects_bad_values(self):
        for value in ["", "01:23:45", "zz:23:45:67:89:ab", "01:23:45:67:89:ab;whoami"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    spoof.normalize_mac_address(value)

    def test_validate_interface_rejects_shell_metacharacters(self):
        self.assertEqual("en0", spoof.validate_interface(" en0 "))
        for value in ["", "en0;reboot", "en0 $(id)", "en0/../../tmp"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    spoof.validate_interface(value)

    def test_parse_mac_address_extracts_and_normalizes(self):
        self.assertEqual(
            "aa:bb:cc:dd:ee:ff",
            spoof.parse_mac_address("ether AA:BB:CC:DD:EE:FF"),
        )

    def test_change_commands_are_argument_lists(self):
        commands = spoof.change_commands(
            "en0",
            "0123456789ab",
            airport_interface="en1",
        )

        self.assertIn(["ifconfig", "en0", "ether", "01:23:45:67:89:ab"], commands)
        for command in commands:
            self.assertIsInstance(command, list)

    def test_set_mac_address_dry_run_does_not_read_current_address(self):
        output = io.StringIO()
        with mock.patch.object(spoof, "get_mac_address") as get_mac_address:
            with redirect_stdout(output):
                spoof.set_mac_address("en0", "0123456789ab", dry_run=True)

        get_mac_address.assert_not_called()
        self.assertIn("Dry run", output.getvalue())
        self.assertIn("ifconfig en0 ether 01:23:45:67:89:ab", output.getvalue())

    def test_resolve_target_defaults_and_manual_values(self):
        args = argparse.Namespace(
            interface=None,
            address=None,
            airport_interface="en1",
        )
        self.assertEqual(("en0", spoof.DEFAULT_WIRED_ADDRESS, "en1"), spoof.resolve_target(args))

        args = argparse.Namespace(
            interface="en2",
            address="aabbccddeeff",
            airport_interface="en0",
        )
        self.assertEqual(("en2", "aabbccddeeff", "en0"), spoof.resolve_target(args))


if __name__ == "__main__":
    unittest.main()
