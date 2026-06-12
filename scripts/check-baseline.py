#!/usr/bin/env python3
"""Static checks for the macOS MAC spoofing utility baseline."""

from pathlib import Path
import ast
import os
import re
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plans/2026-06-08-mac-spoofer-baseline.md"
HOSTED_VALIDATION_PLAN = "docs/plans/2026-06-10-hosted-safe-validation.md"
COMMAND_FAILURE_PLAN = "docs/plans/2026-06-12-command-failure-output-sanitization.md"
REQUIRED = [
    ".github/workflows/check.yml",
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
    "docs/plans/2026-06-09-command-output-type.md",
    "docs/plans/2026-06-09-make-gate-aliases.md",
    "docs/plans/2026-06-09-malformed-command-validation.md",
    "docs/plans/2026-06-09-bytecode-free-verification.md",
    "docs/plans/2026-06-10-whitespace-command-arguments.md",
    "docs/plans/2026-06-10-command-timeout.md",
    HOSTED_VALIDATION_PLAN,
    COMMAND_FAILURE_PLAN,
    "scripts/check-baseline.py",
    "test_spoof_mac_address.py",
]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text, heading):
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


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
        "isinstance(output, str)",
        "normalize_command",
        "command must be a sequence of text arguments",
        "command is required",
        "command arguments must be non-empty text",
        "argument.strip()",
        "COMMAND_TIMEOUT_SECONDS = 15",
        "timeout=COMMAND_TIMEOUT_SECONDS",
        "except subprocess.TimeoutExpired",
        "failed with exit status",
        ") from None",
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
        "test_parse_mac_address_rejects_non_string_output",
        "test_execute_rejects_malformed_commands",
        "ifconfig en0",
        '["ifconfig", " "]',
        "test_execute_uses_bounded_timeout",
        "test_execute_reports_timeout_without_command_arguments",
        "test_execute_reports_failure_without_output_or_command_arguments",
        "host-secret diagnostic",
    ]:
        if phrase not in tests:
            failures.append(f"tests must include {phrase}")

    makefile = read("Makefile")
    for phrase in [
        "PYTHON ?= python3",
        "PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v",
        "compile(pathlib.Path(path).read_text(), path, 'exec')",
        "sh -n SpoofMACAddress",
        "PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check-baseline.py",
        "verify: check",
        "build: test",
        "lint: static-check",
    ]:
        if phrase not in makefile:
            failures.append(f"Makefile must include {phrase}")

    workflow = read(".github/workflows/check.yml")
    for expected in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: ["3.10", "3.12"]',
        "PYTHONDONTWRITEBYTECODE: \"1\"",
        "run: make check",
    ]:
        if expected not in workflow:
            failures.append(f"Check workflow must keep {expected}")

    gitignore = read(".gitignore")
    for phrase in ["__pycache__/", ".env", "*.log", "tmp/"]:
        if phrase not in gitignore:
            failures.append(f".gitignore must include {phrase}")
    bytecode_paths = sorted(
        str(path.relative_to(ROOT))
        for pattern in ("__pycache__", "*.pyc")
        for path in ROOT.rglob(pattern)
    )
    if bytecode_paths:
        failures.append("generated Python bytecode must not remain after gates: " + ", ".join(bytecode_paths[:5]))

    docs = "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md"])
    for phrase in [
        "make check",
        "make lint",
        "make build",
        "make verify",
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
        "command output",
        "malformed command sequences",
        "whitespace-only command arguments",
        "Python bytecode",
        "hosted Linux",
        "bounded command timeout",
        "captured output",
        "exit status",
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
    output_plan = read("docs/plans/2026-06-09-command-output-type.md")
    if "status: completed" not in output_plan or "command output" not in output_plan:
        failures.append("command output type plan must record completed status and verification")
    make_gates_plan = read("docs/plans/2026-06-09-make-gate-aliases.md")
    for phrase in ["status: completed", "make lint", "make build", "make verify"]:
        if phrase not in make_gates_plan:
            failures.append(f"make gate alias plan must record {phrase}")
    malformed_command_plan = read("docs/plans/2026-06-09-malformed-command-validation.md")
    if "status: completed" not in malformed_command_plan or "normalize_command" not in malformed_command_plan:
        failures.append("malformed command validation plan must record completed status and verification")
    bytecode_plan = read("docs/plans/2026-06-09-bytecode-free-verification.md")
    if "status: completed" not in bytecode_plan or "Python bytecode" not in bytecode_plan:
        failures.append("bytecode-free verification plan must record completed status and verification")
    whitespace_command_plan = read("docs/plans/2026-06-10-whitespace-command-arguments.md")
    if (
        "status: completed" not in whitespace_command_plan
        or "whitespace-only command arguments" not in whitespace_command_plan
    ):
        failures.append("whitespace command argument plan must record completed status and verification")
    command_timeout_plan = read("docs/plans/2026-06-10-command-timeout.md")
    if "status: completed" not in command_timeout_plan or "15-second" not in command_timeout_plan:
        failures.append("command timeout plan must record completed status and verification")
    hosted_validation_plan = read(HOSTED_VALIDATION_PLAN)
    if "status: completed" not in hosted_validation_plan or "make check" not in hosted_validation_plan:
        failures.append("hosted safe validation plan must record completed status and verification")
    command_failure_plan = read(COMMAND_FAILURE_PLAN)
    command_failure_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", command_failure_plan
    )
    command_failure_work = markdown_section(command_failure_plan, "Work Completed")
    command_failure_verification = markdown_section(
        command_failure_plan, "Verification Completed"
    )
    if command_failure_status != ["completed"] or not command_failure_work:
        failures.append(
            "command failure sanitization plan must record one completed status and completed work"
        )
    if not command_failure_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", command_failure_verification
    ):
        failures.append(
            "command failure sanitization plan must record finished verification without pending markers"
        )
    for evidence in [
        "make test",
        "make lint",
        "make build",
        "make verify",
        "make check",
        "git diff --check",
        "27398625285",
        "27398635683",
        "8f20cefeb97e7be7dadd026db421d555f5c8f281",
        "failed with exit status",
        "test_execute_reports_failure_without_output_or_command_arguments",
        "host-secret diagnostic",
    ]:
        if evidence not in command_failure_verification:
            failures.append(
                f"command failure sanitization plan must preserve verification evidence: {evidence}"
            )

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
