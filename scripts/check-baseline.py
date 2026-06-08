#!/usr/bin/env python3
"""Static checks for the macOS MAC spoofing utility baseline."""

from pathlib import Path
import ast
import os
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plans/2026-06-08-mac-spoofer-baseline.md"
REQUIRED = [
    ".gitignore",
    "CHANGES.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "SpoofMACAddress",
    "SpoofMACAddress.py",
    "StartupParameters.plist",
    "VISION.md",
    "docs/readme-overview.svg",
    PLAN,
    "scripts/check-baseline.py",
    "test_spoof_mac_address.py",
]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def is_executable(path):
    return bool(os.stat(ROOT / path).st_mode & stat.S_IXUSR)


def main():
    failures = []
    for path in REQUIRED:
        if not (ROOT / path).is_file():
            failures.append(f"required file missing: {path}")

    for path in ["SpoofMACAddress.py", "test_spoof_mac_address.py", "scripts/check-baseline.py"]:
        try:
            ast.parse(read(path), filename=path)
        except SyntaxError as error:
            failures.append(f"{path} must parse as Python: {error}")

    shell_check = subprocess.run(
        ["sh", "-n", "SpoofMACAddress"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if shell_check.returncode != 0:
        failures.append("SpoofMACAddress shell wrapper must pass sh -n")

    for path in ["SpoofMACAddress", "SpoofMACAddress.py"]:
        if not is_executable(path):
            failures.append(f"{path} must remain executable")

    script = read("SpoofMACAddress.py")
    for phrase in [
        "argparse",
        "normalize_mac_address",
        "validate_interface",
        "subprocess.run(",
        "dry_run",
        "unicast",
    ]:
        if phrase not in script:
            failures.append(f"SpoofMACAddress.py must mention {phrase}")
    if "Popen(" in script:
        failures.append("SpoofMACAddress.py must not use raw Popen")
    if "shell=True" in script:
        failures.append("SpoofMACAddress.py must not execute through a shell")

    wrapper = read("SpoofMACAddress")
    for phrase in [
        "SPOOF_MAC_ADDRESS_APPLY",
        "--dry-run",
        "/usr/bin/env python3",
        "SPOOF_MAC_ADDRESS_SCRIPT",
    ]:
        if phrase not in wrapper:
            failures.append(f"SpoofMACAddress wrapper must include {phrase}")

    tests = read("test_spoof_mac_address.py")
    for phrase in [
        "test_normalize_mac_address",
        "test_validate_interface_rejects_shell_metacharacters",
        "test_set_mac_address_dry_run_does_not_read_current_address",
        "01:23:45:67:89:ab",
    ]:
        if phrase not in tests:
            failures.append(f"tests must include {phrase}")

    makefile = read("Makefile")
    for phrase in ["python3 -m unittest discover -v", "sh -n SpoofMACAddress", "scripts/check-baseline.py"]:
        if phrase not in makefile:
            failures.append(f"Makefile must include {phrase}")

    gitignore = read(".gitignore")
    for phrase in ["__pycache__/", ".env", "*.log", "tmp/"]:
        if phrase not in gitignore:
            failures.append(f".gitignore must include {phrase}")

    docs = "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md"])
    for phrase in [
        "make check",
        "--dry-run",
        "SPOOF_MAC_ADDRESS_APPLY=1",
        "explicit local admin tool",
        "MAC address",
        "unicast",
    ]:
        if phrase.lower() not in docs.lower():
            failures.append(f"docs must mention {phrase}")

    plan = read(PLAN)
    if "status: completed" not in plan or "make check" not in plan:
        failures.append("plan must record completed status and verification")

    try:
        ET.parse(ROOT / "docs/readme-overview.svg")
    except ET.ParseError as error:
        failures.append(f"docs/readme-overview.svg must parse as XML: {error}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("OSX-Mac-Spoofer baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
