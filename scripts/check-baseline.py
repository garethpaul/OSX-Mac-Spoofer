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
CHECKOUT_CREDENTIAL_PLAN = "docs/plans/2026-06-12-checkout-credential-boundary.md"
RESTORATION_PLAN = "docs/plans/2026-06-13-hardware-address-restoration.md"
POST_CHANGE_PLAN = "docs/plans/2026-06-13-post-change-address-verification.md"
LOCATION_INDEPENDENT_MAKE_PLAN = "docs/plans/2026-06-14-location-independent-make-gates.md"
PRE_CHANGE_HARDWARE_PLAN = "docs/plans/2026-06-15-pre-change-hardware-capture.md"
PARTIAL_MUTATION_PLAN = "docs/plans/2026-06-15-partial-mutation-error-boundary.md"
MUTATION_COMMAND_ERROR_PLAN = "docs/plans/2026-06-15-mutation-command-error-boundary.md"
POST_MUTATION_VERIFICATION_ERROR_PLAN = "docs/plans/2026-06-15-post-mutation-verification-error.md"
POST_MUTATION_MISMATCH_PLAN = "docs/plans/2026-06-15-post-mutation-mismatch-partial-state.md"
COMMAND_LAUNCH_ERROR_PLAN = "docs/plans/2026-06-17-command-launch-error-boundary.md"
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
    "docs/hardware-address-restoration.md",
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
    CHECKOUT_CREDENTIAL_PLAN,
    RESTORATION_PLAN,
    POST_CHANGE_PLAN,
    LOCATION_INDEPENDENT_MAKE_PLAN,
    PRE_CHANGE_HARDWARE_PLAN,
    PARTIAL_MUTATION_PLAN,
    MUTATION_COMMAND_ERROR_PLAN,
    POST_MUTATION_VERIFICATION_ERROR_PLAN,
    POST_MUTATION_MISMATCH_PLAN,
    COMMAND_LAUNCH_ERROR_PLAN,
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
        "except OSError:",
        'raise RuntimeError(f"{checked_command[0]} could not be started") from None',
        "failed with exit status",
        "if new_address != checked_address:",
        "PARTIAL_STATE_ERROR = (",
        "MISMATCH_PARTIAL_STATE_ERROR = (",
        'address_command = ["ifconfig", checked_interface, "ether", checked_address]',
        "address_changed = False",
        "if address_changed or command == address_command:",
        "network command failed after interface address mutation",
        "inspect and restore state manually",
        ") from None",
    ]:
        if phrase not in script:
            failures.append(f"SpoofMACAddress.py must mention {phrase}")
    if "Popen(" in script:
        failures.append("SpoofMACAddress.py must not use raw Popen")
    if "shell=True" in script:
        failures.append("SpoofMACAddress.py must not execute through a shell")
    set_source = script[script.find("def set_mac_address"):script.find("def build_parser")]
    set_markers = [
        "old_address = get_mac_address(checked_interface)",
        "hardware_address = get_mac_address(checked_interface, hardware=True)",
        'address_command = ["ifconfig", checked_interface, "ether", checked_address]',
        "address_changed = False",
        "    for command in commands:\n        try:\n            execute(command)",
        "            if address_changed or command == address_command:",
        "        if command == address_command:",
        "            address_changed = True",
        "new_address = get_mac_address(checked_interface)",
        "    except (RuntimeError, ValueError):\n        raise RuntimeError(PARTIAL_STATE_ERROR) from None",
        "if new_address != checked_address:\n        raise RuntimeError(MISMATCH_PARTIAL_STATE_ERROR) from None",
        '"Changed {} (h/w: {}) from {} to {}."',
    ]
    if any(marker not in set_source for marker in set_markers) or not all(
        set_source.find(left) < set_source.find(right)
        for left, right in zip(set_markers, set_markers[1:])
    ):
        failures.append(
            "current and hardware lookup must precede mutation and post-change verification"
        )
    verification_lookup_boundary = '''try:
        new_address = get_mac_address(checked_interface)
    except (RuntimeError, ValueError):
        raise RuntimeError(PARTIAL_STATE_ERROR) from None'''
    if verification_lookup_boundary not in set_source:
        failures.append(
            "post-mutation verification lookup must use the sanitized partial-state boundary"
        )
    mismatch_boundary = '''if new_address != checked_address:
        raise RuntimeError(MISMATCH_PARTIAL_STATE_ERROR) from None'''
    if mismatch_boundary not in set_source or set_source.count(
        "raise RuntimeError(PARTIAL_STATE_ERROR) from None"
    ) != 2:
        failures.append(
            "post-mutation mismatch must use its sanitized partial-state boundary"
        )

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
        "test_set_mac_address_rejects_post_change_mismatch_without_identifiers",
        "test_set_mac_address_captures_hardware_before_mutation",
        "test_set_mac_address_hardware_lookup_failure_prevents_mutation",
        "test_set_mac_address_preserves_failure_before_address_mutation",
        "test_set_mac_address_reports_partial_state_after_address_mutation",
        "test_set_mac_address_reports_partial_state_when_mutation_command_fails",
        "test_set_mac_address_reports_partial_state_when_verification_lookup_fails",
        "test_set_mac_address_reports_partial_state_when_verification_output_is_invalid",
        '["current", "hardware", "execute", "execute", "execute", "execute", "current"]',
        "execute.assert_not_called()",
        "self.assertEqual(4, execute.call_count)",
        "self.assertEqual(3, execute.call_count)",
        "self.assertEqual(3, get_mac_address.call_count)",
        "get_mac_address.call_args_list",
        "self.assertIs(failure, raised.exception)",
        "inspect and restore state manually",
        "self.assertTrue(raised.exception.__suppress_context__)",
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
        "test_execute_reports_launch_failure_without_os_details_or_arguments",
        "test_set_mac_address_reports_partial_state_when_mutation_cannot_start",
        'RuntimeError, "ifconfig could not be started"',
        '"/private/path/ifconfig"',
        "host-secret diagnostic",
    ]:
        if phrase not in tests:
            failures.append(f"tests must include {phrase}")
    mismatch_test = tests.split(
        "def test_set_mac_address_rejects_post_change_mismatch_without_identifiers",
        1,
    )[-1].split("def test_set_mac_address_captures_hardware_before_mutation", 1)[0]
    for phrase in [
        '"interface address did not match requested value after mutation"',
        'self.assertNotIn("en0", message)',
        'self.assertNotIn("02:23:45:67:89:ab", message)',
        'self.assertNotIn("02:aa:bb:cc:dd:ee", message)',
        'self.assertIn("inspect and restore state manually", message)',
        "self.assertIsNone(raised.exception.__cause__)",
        "self.assertTrue(raised.exception.__suppress_context__)",
    ]:
        if phrase not in mismatch_test:
            failures.append(
                f"post-mutation mismatch regression must retain {phrase}"
            )

    post_change_docs = {
        "README.md": "success is reported only after the observed interface address matches",
        "SECURITY.md": "Post-change verification should require the observed address to match",
        "VISION.md": "observed post-command address to match the requested target",
        "CHANGES.md": "Verify the observed post-command interface address matches",
    }
    for path, phrase in post_change_docs.items():
        if phrase not in " ".join(read(path).split()):
            failures.append(f"{path} must include {phrase}")
    pre_change_docs = {
        "README.md": "reads the current and hardware addresses before mutation commands begin",
        "SECURITY.md": "Current and hardware address lookup should complete before mutation commands begin",
        "VISION.md": "Capture current and hardware addresses before mutation commands begin",
        "CHANGES.md": "Capture current and hardware addresses before mutation commands begin",
    }
    for path, phrase in pre_change_docs.items():
        if phrase not in " ".join(read(path).split()):
            failures.append(f"{path} must include {phrase}")
    partial_state_docs = {
        "README.md": "reports a sanitized partial-state error and requires manual inspection and restoration",
        "SECURITY.md": "Failures after the address mutation should report a sanitized partial state",
        "VISION.md": "Surface post-mutation command failures as sanitized partial state",
        "CHANGES.md": "Report later command failures as an identifier-free partial mutation state",
    }
    for path, phrase in partial_state_docs.items():
        if phrase not in " ".join(read(path).split()):
            failures.append(f"{path} must include {phrase}")
    mutation_command_docs = {
        "README.md": "A failure from the address mutation command itself is also treated as a possible partial state",
        "SECURITY.md": "Failure of the address mutation command itself should be treated as a possible partial state",
        "VISION.md": "Treat address mutation command failures as possible partial state",
        "CHANGES.md": "Treat failure of the address mutation command itself as a possible partial state",
    }
    for path, phrase in mutation_command_docs.items():
        if phrase not in " ".join(read(path).split()):
            failures.append(f"{path} must include {phrase}")
    verification_error_docs = {
        "README.md": "Failure of the final verification lookup is likewise reported as sanitized partial state",
        "SECURITY.md": "Failure of the final verification lookup should report sanitized partial state",
        "VISION.md": "Treat final verification lookup failures as sanitized partial state",
        "CHANGES.md": "Report final verification lookup failures as identifier-free partial state",
    }
    for path, phrase in verification_error_docs.items():
        if phrase not in " ".join(read(path).split()):
            failures.append(f"{path} must include {phrase}")
    mismatch_partial_state_docs = {
        "README.md": "post-mutation mismatch is reported as sanitized partial state requiring manual inspection and restoration",
        "SECURITY.md": "post-mutation address mismatch should report sanitized partial state",
        "VISION.md": "Treat post-mutation address mismatches as sanitized partial state",
        "CHANGES.md": "Report post-mutation address mismatches through the same identifier-free partial-state recovery boundary",
    }
    for path, phrase in mismatch_partial_state_docs.items():
        if phrase not in " ".join(read(path).split()):
            failures.append(f"{path} must include {phrase}")
    for path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]:
        if "command launch error handling" not in read(path).lower():
            failures.append(f"{path} must document command launch error handling")
    changes = " ".join(read("CHANGES.md").split())
    if "source compilation, shell syntax, and checker paths" not in changes:
        failures.append(
            "CHANGES.md must record rooted source, shell, and checker paths"
        )

    makefile = read("Makefile")
    for phrase in [
        "PYTHON ?= python3",
        "override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))",
        'PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v -s "$(REPO_ROOT)"',
        'REPO_ROOT="$(REPO_ROOT)" PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -c',
        "root = pathlib.Path(os.environ['REPO_ROOT'])",
        "compile((root / path).read_text(), path, 'exec')",
        'sh -n "$(REPO_ROOT)/SpoofMACAddress"',
        'PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(REPO_ROOT)/scripts/check-baseline.py"',
        "verify: check",
        "build: test",
        "lint: static-check",
    ]:
        if phrase not in makefile:
            failures.append(f"Makefile must include {phrase}")

    workflow = read(".github/workflows/check.yml")
    workflow_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / ".github/workflows").iterdir()
        if path.is_file()
    )
    checkout_step = (
        "      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10\n"
        "        with:\n"
        "          persist-credentials: false"
    )
    if workflow_files != [".github/workflows/check.yml"]:
        failures.append("workflow inventory must contain only .github/workflows/check.yml")
    if workflow.count("actions/checkout@") != 1 or checkout_step not in workflow:
        failures.append("Check workflow must use one pinned credential-free checkout")
    if workflow.count("persist-credentials:") != 1 or "persist-credentials: true" in workflow:
        failures.append("Check workflow must not persist checkout credentials")
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
        "absolute path works externally",
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
    checkout_credential_plan = read(CHECKOUT_CREDENTIAL_PLAN)
    if (
        "status: completed" not in checkout_credential_plan.lower()
        or "persist-credentials: false" not in checkout_credential_plan
        or "hostile mutations rejected" not in checkout_credential_plan
    ):
        failures.append("checkout credential plan must record completed verification")
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

    restoration = " ".join(read("docs/hardware-address-restoration.md").split())
    for phrase in [
        "Review date: 2026-06-13",
        "authorized operator restoring one known macOS network interface",
        "current address",
        "hardware address",
        "locally administered unicast address",
        "approved private operational record",
        'networksetup -getmacaddress "$INTERFACE"',
        'ifconfig "$INTERFACE" | awk',
        'SpoofMACAddress.py "$INTERFACE" 02:23:45:67:89:ab --dry-run',
        "Dry-run mode must remain subprocess-free",
        'sudo ifconfig "$INTERFACE" ether "$HARDWARE_ADDRESS"',
        "networksetup -detectnewhardware",
        "intentionally separate from `SpoofMACAddress.py`",
        "must continue to reject globally administered addresses",
        "current address matches the recorded hardware address",
        "applicable access-control, inventory, and network-policy checks pass",
        "no startup wrapper or other automation",
        "Stop rather than trying unrelated interfaces or addresses",
        "Never add automatic startup restoration, hidden persistence",
    ]:
        if phrase not in restoration:
            failures.append(f"hardware restoration guidance must include {phrase}")

    restoration_plan = read(RESTORATION_PLAN)
    restoration_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", restoration_plan)
    restoration_work = markdown_section(restoration_plan, "Work Completed")
    restoration_verification = markdown_section(
        restoration_plan, "Verification Completed"
    )
    if restoration_status != ["completed"] or not restoration_work:
        failures.append(
            "hardware restoration plan must record one completed status and completed work"
        )
    if not restoration_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", restoration_verification
    ):
        failures.append("hardware restoration plan must record completed verification")
    for evidence in [
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "external working directory",
        "workflow YAML",
        "StartupParameters.plist",
        "hostile mutations rejected",
        "implementation and test paths had no diff",
        "git diff --check",
        "secret, captured-identifier, and generated-artifact scan",
    ]:
        if evidence not in restoration_verification:
            failures.append(f"hardware restoration verification must record {evidence}")

    post_change_plan = read(POST_CHANGE_PLAN)
    post_change_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", post_change_plan)
    post_change_work = markdown_section(post_change_plan, "Work Completed")
    post_change_verification = markdown_section(
        post_change_plan, "Verification Completed"
    )
    if post_change_status != ["completed"] or not post_change_work:
        failures.append(
            "post-change verification plan must record completed status and work"
        )
    if not post_change_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", post_change_verification
    ):
        failures.append("post-change verification plan must record completed verification")
    for evidence in [
        "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_spoof_mac_address.py",
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "external working directory",
        "workflow YAML",
        "StartupParameters.plist",
        "hostile mutations",
        "git diff --check",
        "secret and generated-artifact scan",
    ]:
        if evidence not in post_change_verification:
            failures.append(f"post-change verification must record {evidence}")

    location_make_plan = read(LOCATION_INDEPENDENT_MAKE_PLAN)
    location_make_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", location_make_plan
    )
    location_make_work = markdown_section(location_make_plan, "Work Completed")
    location_make_verification = markdown_section(
        location_make_plan, "Verification Completed"
    )
    if location_make_status != ["completed"] or not location_make_work:
        failures.append(
            "location-independent Make plan must record one completed status "
            "and completed work"
        )
    if not location_make_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", location_make_verification
    ):
        failures.append(
            "location-independent Make plan must record completed verification"
        )
    for evidence in [
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "make static-check",
        "16 mocked, non-privileged tests",
        "from `/tmp`",
        "absolute",
        "caller-supplied `REPO_ROOT=/tmp`",
        "caller-relative `PYTHON=./osx-mac-python`",
        "Python source compilation",
        "workflow YAML parsing",
        "rooted shell syntax",
        "StartupParameters.plist",
        "Thirteen isolated hostile mutations were rejected",
    ]:
        if evidence not in location_make_verification:
            failures.append(
                f"location-independent Make verification must record {evidence}"
            )

    pre_change_plan = read(PRE_CHANGE_HARDWARE_PLAN)
    pre_change_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", pre_change_plan)
    pre_change_work = markdown_section(pre_change_plan, "Work Completed")
    pre_change_verification = markdown_section(
        pre_change_plan, "Verification Completed"
    )
    if pre_change_status != ["completed"] or not pre_change_work:
        failures.append(
            "pre-change hardware capture plan must record completed status and work"
        )
    if not pre_change_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", pre_change_verification
    ):
        failures.append(
            "pre-change hardware capture plan must record completed verification"
        )
    for evidence in [
        "18 mocked, non-privileged tests",
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "external working directory",
        "hostile mutations",
        "git diff --check",
        "secret and generated-artifact scan",
    ]:
        if evidence not in pre_change_verification:
            failures.append(
                f"pre-change hardware capture verification must record {evidence}"
            )

    partial_mutation_plan = read(PARTIAL_MUTATION_PLAN)
    partial_mutation_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", partial_mutation_plan
    )
    partial_mutation_work = markdown_section(
        partial_mutation_plan, "Work Completed"
    )
    partial_mutation_verification = markdown_section(
        partial_mutation_plan, "Verification Completed"
    )
    if (partial_mutation_status != ["completed"] or not partial_mutation_work or
            not partial_mutation_verification or re.search(
                r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                partial_mutation_verification,
            )):
        failures.append(
            "partial mutation error plan must record completed verification"
        )
    for evidence in [
        "20 mocked, non-privileged unit tests",
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "external working directory",
        "Six isolated hostile mutations",
        "git diff --check",
    ]:
        if evidence not in partial_mutation_verification:
            failures.append(
                f"partial mutation error verification must record {evidence}"
            )

    mutation_command_plan = read(MUTATION_COMMAND_ERROR_PLAN)
    mutation_command_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", mutation_command_plan
    )
    mutation_command_work = markdown_section(
        mutation_command_plan, "Work Completed"
    )
    mutation_command_verification = markdown_section(
        mutation_command_plan, "Verification Completed"
    )
    if (mutation_command_status != ["completed"] or not mutation_command_work or
            not mutation_command_verification or re.search(
                r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                mutation_command_verification,
            )):
        failures.append(
            "mutation command error plan must record completed verification"
        )
    for evidence in [
        "21 mocked, non-privileged unit tests",
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "external working directory",
        "Five isolated hostile mutations",
        "git diff --check",
    ]:
        if evidence not in mutation_command_verification:
            failures.append(
                f"mutation command error verification must record {evidence}"
            )

    verification_error_plan = read(POST_MUTATION_VERIFICATION_ERROR_PLAN)
    verification_error_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", verification_error_plan
    )
    verification_error_work = markdown_section(
        verification_error_plan, "Work Completed"
    )
    verification_error_verification = markdown_section(
        verification_error_plan, "Verification Completed"
    )
    if (verification_error_status != ["completed"] or not verification_error_work or
            not verification_error_verification or re.search(
                r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                verification_error_verification,
            )):
        failures.append(
            "post-mutation verification error plan must record completed verification"
        )
    for evidence in [
        "mocked, non-privileged unit tests",
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "external working directory",
        "isolated hostile mutations",
        "git diff --check",
    ]:
        if evidence not in verification_error_verification:
            failures.append(
                f"post-mutation verification error verification must record {evidence}"
            )

    mismatch_plan = read(POST_MUTATION_MISMATCH_PLAN)
    mismatch_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", mismatch_plan)
    mismatch_work = markdown_section(mismatch_plan, "Work Completed")
    mismatch_verification = markdown_section(mismatch_plan, "Verification Completed")
    if (mismatch_status != ["completed"] or not mismatch_work or
            not mismatch_verification or re.search(
                r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                mismatch_verification,
            )):
        failures.append(
            "post-mutation mismatch plan must record completed verification"
        )
    for evidence in [
        "23 mocked, non-privileged unit tests",
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "external working directory",
        "Six isolated hostile mutations",
        "Exact diff",
    ]:
        if evidence not in mismatch_verification:
            failures.append(
                f"post-mutation mismatch verification must record {evidence}"
            )

    launch_error_plan = read(COMMAND_LAUNCH_ERROR_PLAN)
    launch_error_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", launch_error_plan)
    launch_error_verification = markdown_section(
        launch_error_plan, "Verification Completed"
    )
    if (launch_error_status != ["completed"] or
            "two focused command launch regressions passed" not in launch_error_verification or
            "25 mocked, non-privileged unit tests" not in launch_error_verification or
            "All Make aliases passed" not in launch_error_verification or
            "external directory" not in launch_error_verification or
            "Six isolated hostile mutations were rejected" not in launch_error_verification or
            re.search(r"(?i)\b(?:pending|todo|tbd|not run|to be recorded)\b",
                      launch_error_verification)):
        failures.append(
            "command launch error boundary plan must record completed verification"
        )

    guidance = " ".join(
        "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]).split()
    ).lower()
    if (
        "checkout credentials are not persisted" not in guidance
        or "credential-free checkout" not in guidance
    ):
        failures.append("repository guidance must document the credential-free checkout boundary")
    if "source compilation, shell syntax, and checker paths" not in guidance:
        failures.append(
            "repository guidance must document rooted Make path resolution"
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
