# Command Failure Output Sanitization

status: completed

## Context

Platform commands run with validated argument lists and bounded timeouts, but a
nonzero result currently copies captured standard error or standard output into
the raised exception. Those streams can contain interface names, MAC addresses,
or other host-specific details that should not be repeated by the command-line
error path.

## Objectives

- Report the failed executable and numeric exit status without including command
  arguments or captured output.
- Preserve successful command output, dry-run behavior, and timeout
  sanitization.
- Add mocked regression coverage containing sensitive argument, stdout, and
  stderr values.
- Extend the static baseline and operator documentation to enforce the contract.

## Implementation Units

Files:

- `SpoofMACAddress.py`
- `test_spoof_mac_address.py`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Replace the nonzero-result detail forwarding with a deterministic error that
contains only the executable and exit status. Verify that exception chaining is
suppressed and that sensitive captured values are absent. Record the behavior
in the maintained documentation and make the canonical checker reject removal
of either the implementation or regression test.

## Work Completed

- Replaced captured-output forwarding with a deterministic error containing
  only the executable name and numeric exit status.
- Suppressed exception chaining so subprocess details are not appended to the
  command-line error.
- Added a mocked regression fixture containing sensitive command arguments,
  standard output, and standard error without running platform commands.
- Updated the maintained operator documentation and static checker contract.

## Verification Completed

- Focused mocked nonzero-command failure and timeout tests passed.
- `make test` passed all 15 mocked tests without privileged operations.
- `make lint`, `make build`, `make verify`, and `make check` passed.
- Hostile static-check mutations for implementation and test removal were
  rejected.
- `git diff --check` passed.
- GitHub Actions push run `27398625285` and pull-request run `27398635683`
  completed successfully on implementation head
  `8f20cefeb97e7be7dadd026db421d555f5c8f281` for Python 3.10 and 3.12.
- `SpoofMACAddress.py` raises `failed with exit status` from `None`, and
  `test_execute_reports_failure_without_output_or_command_arguments` verifies
  that the `host-secret diagnostic` fixture is not exposed.

## Boundaries

- Do not execute macOS networking commands or privileged operations.
- Do not change command arguments, sequencing, defaults, or successful output.
- Do not add dependencies.
