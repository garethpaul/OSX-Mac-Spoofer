#!/usr/bin/env python3
import os
from pathlib import Path
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
            return subprocess.run(
                ["make", "--no-print-directory", "-n", "-f", str(makefile), *arguments],
                cwd=checkout.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, check=False, env=env,
            )

    def test_all_targets_preserve_spaced_absolute_makefile_path(self):
        targets = ("build", "check", "lint", "root-test", "static-check", "test", "verify")
        for target in targets:
            for name, arguments, environment in (
                ("none", (target,), None),
                ("command", (target, "REPO_ROOT=/tmp/attacker-root"), None),
                ("environment", (target,), {"REPO_ROOT": "/tmp/attacker-root"}),
            ):
                with self.subTest(target=target, override=name):
                    result = self.run_make(*arguments, environment=environment)
                    self.assertEqual(result.returncode, 0, result.stdout)
                    self.assertNotIn("/tmp/attacker-root", result.stdout)
                    self.assertIn("OSX Mac Spoofer's [gate] ", result.stdout)

    def test_command_line_makefile_list_override_fails_closed(self):
        result = self.run_make("verify", "MAKEFILE_LIST=/tmp/untrusted")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

    def test_environment_makefile_list_override_fails_closed(self):
        result = self.run_make("-e", "verify", environment={"MAKEFILE_LIST": "/tmp/untrusted"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

if __name__ == "__main__":
    unittest.main()
