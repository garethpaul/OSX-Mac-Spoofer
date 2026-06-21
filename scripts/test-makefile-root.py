#!/usr/bin/env python3
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class MakefileRootTests(unittest.TestCase):
    def run_make(self, *arguments, environment=None):
        with tempfile.TemporaryDirectory(prefix="OSX Mac Spoofer's [gate] ") as directory:
            checkout = Path(directory)
            makefile = checkout / "Makefile"
            makefile.write_text((ROOT / "Makefile").read_text(encoding="utf-8"), encoding="utf-8")
            env = {"PATH": os.environ.get("PATH", "")}
            if environment:
                env.update(environment)
            result = subprocess.run(
                ["make", "--no-print-directory", "-n", "-f", str(makefile), *arguments],
                cwd=checkout.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, check=False, env=env,
            )
            return result, shlex.quote(str(checkout.resolve()))

    def assert_live_root_path_is_literal(self, checkout_name, marker_name):
        with tempfile.TemporaryDirectory() as parent:
            checkout = Path(parent) / checkout_name
            scripts = checkout / "scripts"
            scripts.mkdir(parents=True)
            makefile = checkout / "Makefile"
            makefile.write_text((ROOT / "Makefile").read_text(encoding="utf-8"), encoding="utf-8")
            (scripts / "test-makefile-root.py").write_text(
                "print('live root stub passed')\n", encoding="utf-8"
            )
            result = subprocess.run(
                ["make", "--no-print-directory", "-f", str(makefile), "root-test"],
                cwd=checkout.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, check=False, env={"PATH": os.environ.get("PATH", "")},
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertFalse((checkout.parent / marker_name).exists(), result.stdout)
            self.assertIn("live root stub passed", result.stdout)

    def test_all_targets_preserve_spaced_absolute_makefile_path(self):
        targets = ("build", "check", "lint", "root-test", "static-check", "test", "verify")
        for target in targets:
            for name, arguments, environment in (
                ("none", (target,), None),
                ("command", (target, "REPO_ROOT=/tmp/attacker-root"), None),
                ("environment", (target,), {"REPO_ROOT": "/tmp/attacker-root"}),
            ):
                with self.subTest(target=target, override=name):
                    result, expected_root = self.run_make(*arguments, environment=environment)
                    self.assertEqual(result.returncode, 0, result.stdout)
                    self.assertNotIn("/tmp/attacker-root", result.stdout)
                    self.assertIn(expected_root, result.stdout)

    def test_command_line_makefile_list_override_fails_closed(self):
        result, _ = self.run_make("verify", "MAKEFILE_LIST=/tmp/untrusted")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

    def test_environment_makefile_list_override_fails_closed(self):
        result, _ = self.run_make("-e", "verify", environment={"MAKEFILE_LIST": "/tmp/untrusted"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

    def test_live_root_path_does_not_execute_shell_metacharacters(self):
        for checkout_name, marker_name in (
            ("OSX backtick `touch BACKTICK_PWNED` case", "BACKTICK_PWNED"),
            ('OSX quote " ; touch QUOTE_PWNED ; echo " case', "QUOTE_PWNED"),
        ):
            with self.subTest(checkout_name=checkout_name):
                self.assert_live_root_path_is_literal(checkout_name, marker_name)

if __name__ == "__main__":
    unittest.main()
