# Post-Mutation Verification Error Boundary

status: completed

## Context

After all four network mutation commands complete, `set_mac_address` reads the
interface again to verify the requested address. If that lookup times out or
fails, its raw exception escapes even though network state may already have
changed, exposing command context and omitting restoration guidance.

## Goal

Treat failure of the final observed-address lookup as sanitized partial state
that requires manual inspection and restoration.

## Scope

- Route execution and output-validation errors from the final current-address
  lookup through the existing partial-state message.
- Suppress the original exception context so interface names, target addresses,
  and command output do not escape.
- Preserve pre-mutation lookup failures, mutation-command boundaries, the
  successful output, and the existing address-mismatch error.
- Add mocked regression coverage, mutation-sensitive static contracts,
  synchronized guidance, and completed verification evidence.

## Implementation Units

### U1: Guard post-mutation verification lookup

Files: `SpoofMACAddress.py`, `test_spoof_mac_address.py`

Catch only the final lookup's execution or parse failure after mutation and
reuse the established sanitized partial-state result.

### U2: Lock the boundary into verification

Files: `scripts/check-baseline.py`, `README.md`, `SECURITY.md`, `VISION.md`,
`CHANGES.md`, `docs/plans/2026-06-15-post-mutation-verification-error.md`

Require the exact runtime boundary, the no-secret regression, synchronized
operator guidance, and truthful completed evidence.

## Verification Plan

- Run the focused error-boundary tests and complete mocked unit suite.
- Run all Make gates from the repository and through the absolute Makefile path
  externally on available Python 3.10 and 3.12 runtimes.
- Reject isolated mutations of the lookup boundary, context suppression,
  regression, guidance, and plan status.
- Audit the exact diff for bytecode, dependency changes, credentials, binaries,
  modes, and unintended paths.

## Scope Boundaries

- Do not execute privileged commands or add automatic rollback.
- Do not expose interface/address identifiers or change address normalization.

## Work Completed

- Wrapped final observed-address execution and parse failures in the established
  sanitized partial-state boundary after all mutation commands complete.
- Suppressed the original lookup exception context while preserving the
  existing mismatch result and every pre-mutation error path.
- Added a no-secret mocked regression, static contracts, and synchronized
  operator guidance.

## Verification Completed

- The focused verification-lookup regressions and all 23 mocked, non-privileged unit tests
  passed on the available Python 3.12 runtime.
- `make lint`, `make test`, `make build`, `make verify`, and `make check` passed
  from the repository and through the absolute Makefile path from an external working directory.
- Five isolated hostile mutations covering the lookup boundary, context
  suppression, regression, guidance, and completed plan status were rejected.
- `git diff --check` and explicit bytecode, dependency, credential, binary,
  mode, and intended-path audits passed.
