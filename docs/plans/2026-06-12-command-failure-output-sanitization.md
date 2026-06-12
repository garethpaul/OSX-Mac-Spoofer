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

## Verification

- Focused mocked nonzero-command failure and timeout tests passed.
- `make test` passed all 15 mocked tests without privileged operations.
- `make lint`, `make build`, `make verify`, and `make check` passed.
- Hostile static-check mutations for implementation and test removal were
  rejected.
- `git diff --check` passed.

## Boundaries

- Do not execute macOS networking commands or privileged operations.
- Do not change command arguments, sequencing, defaults, or successful output.
- Do not add dependencies.
