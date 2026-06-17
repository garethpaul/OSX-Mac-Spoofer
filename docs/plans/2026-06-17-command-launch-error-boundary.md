# Command Launch Error Boundary

status: completed

## Problem

`execute` converts timeouts and nonzero command exits into controlled runtime
errors, but `subprocess.run` can also raise `OSError` when an executable is
missing, inaccessible, or cannot be launched. That exception currently escapes
the CLI's controlled error path and may produce a traceback containing host
details instead of a concise operator diagnostic.

## Prioritized Requirements

- P0. Convert command-launch `OSError` failures into a controlled
  `RuntimeError` that identifies only the executable and does not expose command
  arguments, exception text, paths supplied by the OS, or chained context.
- P0. Preserve the existing post-mutation partial-state boundary: launch errors
  after or during the address mutation must still require manual inspection and
  restoration without identifiers.
- P1. Preserve timeout, nonzero-exit, dry-run, validation, pre-change capture,
  post-change verification, and mismatch behavior.
- P1. Add mutation-sensitive mocked tests, static contracts, synchronized
  operator guidance, and completed verification evidence.

## Implementation Units

### U1. Sanitize executable launch failures

**Files:** `SpoofMACAddress.py`

Catch `OSError` around `subprocess.run` and raise a context-suppressed runtime
error naming only `checked_command[0]`. Keep timeout and nonzero-exit diagnostics
unchanged.

### U2. Mocked regression coverage

**Files:** `test_spoof_mac_address.py`

Prove a direct launch failure is controlled, omits sensitive exception and
argument text, and suppresses chaining. Prove an address-command launch failure
continues to report sanitized partial state through `set_mac_address`.

### U3. Static contracts and guidance

**Files:** `scripts/check-baseline.py`, `README.md`, `SECURITY.md`, `VISION.md`,
`CHANGES.md`, `docs/plans/2026-06-17-command-launch-error-boundary.md`

Protect the `OSError` boundary, both regressions, synchronized guidance, and
completed plan evidence against isolated hostile mutations.

## Validation

- Run focused launch/partial-state cases, the full mocked suite, every Make
  alias, shell syntax, Python compilation, and the absolute Makefile check from
  an external directory.
- Reject isolated mutations of the catch, sanitized message, context
  suppression, regressions, guidance, and completed plan status.
- Audit the exact stacked diff, generated artifacts, credentials, conflict
  markers, modes, binaries, large files, and whitespace before committing.

## Scope Boundaries

- Do not execute privileged networking commands or change command ordering,
  command arguments, timeout duration, target defaults, or address validation.
- Do not expose raw OS exception text or command arguments in user-facing
  diagnostics.
- Do not merge or close any stacked pull request.

## Work Completed

- Converted command-launch `OSError` failures into context-suppressed runtime
  errors that name only the executable.
- Preserved the post-mutation partial-state wrapper so an address-command launch
  failure cannot imply the interface remained unchanged.
- Added direct and mutation-path regressions, static contracts, synchronized
  operator guidance, and this completed evidence record.

## Verification Completed

- two focused command launch regressions passed for direct execution and
  address-mutation partial state.
- The complete suite passed with 25 mocked, non-privileged unit tests.
- All Make aliases passed, including the absolute Makefile check from an
  external directory; shell syntax and Python compilation also passed.
- Six isolated hostile mutations were rejected for the catch, sanitized message,
  context suppression, regression registration, guidance, and plan status.
- The exact diff, generated-artifact, credential-signature, conflict-marker,
  mode, binary, large-file, and whitespace audits passed.

## Risks

- Real macOS authorization and networking behavior remain outside the Linux
  mocked test boundary.
- The executable name remains visible, consistent with existing timeout and
  nonzero-exit diagnostics.
- This change is stacked on PR #13, which must remain open and merge first.
