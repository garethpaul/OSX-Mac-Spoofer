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
    "docs/plans/2026-06-09-nonzero-mac-validation.md",
    "docs/plans/2026-06-09-local-admin-mac-validation.md",
    "docs/plans/2026-06-09-observed-mac-normalization.md",
    "docs/plans/2026-06-09-interface-option-validation.md",
    "docs/plans/2026-06-09-non-string-validator-inputs.md",
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
        "normalize_observed_mac_address",
        "validate_interface",
        "subprocess.run(",
        "dry_run",
        "unicast",
        "all zeroes",
        "locally administered",
        "interface must not start with a dash",
        "isinstance(address, str)",
        "isinstance(interface, str)",
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
        "test_normalize_observed_mac_address_accepts_hardware_addresses",
        "test_validate_interface_rejects_shell_metacharacters",
        "test_set_mac_address_dry_run_does_not_read_current_address",
        "00:00:00:00:00:00",
        "01:23:45:67:89:ab",
        "00:23:45:67:89:ab",
        "--help",
        "test_normalize_mac_address_rejects_non_string_values",
        "test_validate_interface_rejects_non_string_values",
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
        "nonzero",
        "locally administered",
        "observed",
        "dash",
        "non-string",
    ]:
        if phrase.lower() not in docs.lower():
            failures.append(f"docs must mention {phrase}")

    plan = read(PLAN)
    if "status: completed" not in plan or "make check" not in plan:
        failures.append("plan must record completed status and verification")
    nonzero_plan = read("docs/plans/2026-06-09-nonzero-mac-validation.md")
    if "status: completed" not in nonzero_plan or "00:00:00:00:00:00" not in nonzero_plan:
        failures.append("nonzero MAC plan must record completed status and verification")
    local_admin_plan = read("docs/plans/2026-06-09-local-admin-mac-validation.md")
    if "status: completed" not in local_admin_plan or "locally administered" not in local_admin_plan:
        failures.append("local-admin MAC plan must record completed status and verification")
    observed_plan = read("docs/plans/2026-06-09-observed-mac-normalization.md")
    if "status: completed" not in observed_plan or "normalize_observed_mac_address" not in observed_plan:
        failures.append("observed MAC plan must record completed status and verification")
    interface_plan = read("docs/plans/2026-06-09-interface-option-validation.md")
    if "status: completed" not in interface_plan or "--help" not in interface_plan:
        failures.append("interface option plan must record completed status and verification")
    non_string_plan = read("docs/plans/2026-06-09-non-string-validator-inputs.md")
    if "status: completed" not in non_string_plan or "non-string" not in non_string_plan:
        failures.append("non-string validator input plan must record completed status and verification")

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
