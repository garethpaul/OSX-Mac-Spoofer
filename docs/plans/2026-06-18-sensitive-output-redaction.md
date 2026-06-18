# Sensitive Output Redaction

status: planned

## Problem

The command boundary now sanitizes launch and mutation failures, but successful
and dry-run paths still print network identifiers. Dry-run output renders the
full `ifconfig ... ether <address>` command, and successful mutation output
prints the interface, hardware address, previous address, and requested
address. CodeQL reports both output paths as high-severity clear-text logging of
sensitive data.

## Prioritized Requirements

- P0. Prevent dry-run output from printing the requested MAC address or other
  command arguments while retaining enough information to show command order.
- P0. Prevent successful mutation output from printing interface names,
  hardware addresses, previous addresses, or requested/observed addresses.
- P1. Preserve input validation, command ordering, pre-mutation current and
  hardware capture, mutation behavior, post-change verification, partial-state
  errors, and context-suppressed diagnostics.
- P1. Add mutation-sensitive tests and static contracts for both output paths,
  synchronized operator guidance, and completed verification evidence.

## Implementation Units

### U1. Redact dry-run command output

**Files:** `SpoofMACAddress.py`

Replace full command rendering with a stable executable-only dry-run message.
Keep validated list-form commands and the existing no-mutation behavior.

### U2. Redact successful mutation output

**Files:** `SpoofMACAddress.py`

Replace address-bearing success and follow-up text with identifier-free success
and restoration guidance. Continue capturing pre-change current and hardware
addresses before mutation so failure boundaries retain the same ordering and
state awareness.

### U3. Regression contracts and guidance

**Files:** `test_spoof_mac_address.py`, `scripts/check-baseline.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-18-sensitive-output-redaction.md`

Prove both output paths omit every interface and MAC value while preserving
command order and success behavior. Protect the implementation, tests,
guidance, and completed plan evidence against isolated hostile mutations.

## Validation

- Run focused dry-run and successful-mutation tests, the full mocked suite,
  every Make alias, shell syntax, Python compilation, and the absolute Makefile
  check from an external directory.
- Reject isolated mutations that restore full command rendering, interface or
  address output, weaken the focused regressions, remove guidance, or leave the
  plan incomplete.
- Audit the exact stacked diff, generated artifacts, credential signatures,
  conflict markers, modes, binaries, large files, and whitespace before
  committing.

## Scope Boundaries

- Do not execute privileged networking commands or change command ordering,
  command arguments, timeout duration, target defaults, address validation, or
  post-mutation verification.
- Do not remove pre-mutation current and hardware address capture; it remains an
  ordering and recovery boundary even though values are no longer printed.
- Do not merge or close any stacked pull request.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation.

## Risks

- Redacted output provides less interactive detail; operators can still inspect
  local state explicitly with platform tools when needed.
- Real macOS authorization, interface mutation, and restoration remain outside
  the Linux mocked test boundary.
- This change is stacked on PR #14, which must remain open and merge first.
