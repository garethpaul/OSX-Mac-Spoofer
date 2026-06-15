# Post-Mutation Verification Error Boundary

status: planned

## Context

After all four network mutation commands complete, `set_mac_address` reads the
interface again to verify the requested address. If that lookup times out or
fails, its raw exception escapes even though network state may already have
changed, exposing command context and omitting restoration guidance.

## Goal

Treat failure of the final observed-address lookup as sanitized partial state
that requires manual inspection and restoration.

## Scope

- Route a `RuntimeError` from the final current-address lookup through the
  existing partial-state message.
- Suppress the original exception context so interface names, target addresses,
  and command output do not escape.
- Preserve pre-mutation lookup failures, mutation-command boundaries, the
  successful output, and the existing address-mismatch error.
- Add mocked regression coverage, mutation-sensitive static contracts,
  synchronized guidance, and completed verification evidence.

## Implementation Units

### U1: Guard post-mutation verification lookup

Files: `SpoofMACAddress.py`, `test_spoof_mac_address.py`

Catch only the final lookup's runtime failure after mutation and reuse the
established sanitized partial-state result.

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
