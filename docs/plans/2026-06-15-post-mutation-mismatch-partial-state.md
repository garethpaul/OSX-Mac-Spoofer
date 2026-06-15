# Post-Mutation Mismatch Partial State

Status: planned

## Summary

Treat an observed post-command MAC address mismatch as the same sanitized
partial state used for command and verification lookup failures after mutation.
The utility must not imply a clean failure when the interface may hold an
unexpected address.

## Problem Frame

`set_mac_address` currently rejects an observed address that differs from the
validated target, but its concise mismatch error does not tell the operator to
inspect and restore the interface. All mutation commands have already run at
that point, so the resulting state is uncertain and operational recovery is
required.

## Requirements

- R1: Report post-mutation address mismatch as a possible partial state.
- R2: Require manual inspection and restoration without exposing interface or
  MAC identifiers.
- R3: Preserve command order, pre-mutation lookups, successful output, dry-run
  behavior, and all existing command/lookup failure boundaries.
- R4: Add mutation-sensitive mocked coverage and synchronized guidance.

## Key Technical Decisions

- Reuse the existing identifier-free partial-state message rather than adding a
  second recovery contract.
- Keep mismatch detection after the final observed-address lookup and before
  any success output.
- Do not attempt automatic rollback because the actual interface state and
  platform command outcome are not known reliably.

## Implementation Units

### U1. Align Mismatch Failure Semantics

**Goal:** Route an observed target mismatch through the established
partial-state recovery message.

**Requirements:** R1, R2, R3

**Files:** `SpoofMACAddress.py`, `test_spoof_mac_address.py`

**Approach:** Preserve the equality check and replace only the mismatch error
contract. Extend the existing mocked mismatch regression to require recovery
guidance, context suppression, and identifier redaction.

**Test scenarios:**
- Four mutation commands complete, final lookup returns a different valid MAC,
  and the function raises the sanitized partial-state error.
- The error omits the interface, requested address, observed address, and any
  chained exception context.
- Matching final address still prints the existing success output.

**Verification:** The focused mismatch test and complete mocked suite pass with
no privileged command execution.

### U2. Enforce And Document The Boundary

**Goal:** Make the mismatch recovery contract mutation-visible and durable.

**Requirements:** R4

**Dependencies:** U1

**Files:** `scripts/check-baseline.py`, `README.md`, `SECURITY.md`, `VISION.md`,
`CHANGES.md`, `docs/plans/2026-06-15-post-mutation-mismatch-partial-state.md`

**Approach:** Require source/test ordering, canonical recovery wording,
completed plan evidence, and consistent operator guidance.

**Test scenarios:** Reject isolated mutations that restore the old mismatch
message, remove recovery assertions or redaction, remove guidance, or leave the
plan incomplete.

**Verification:** All Make gates pass from the repository and an external
working directory; exact diff and artifact/security audits remain clean.

## Scope Boundaries

- No privileged macOS networking command will be executed on this Linux host.
- No command order, interface validation, MAC normalization, timeout, default,
  launcher, dependency, or configuration behavior changes.
- Automatic rollback remains out of scope because it could compound an unknown
  network state.
- The change remains stacked on PR #12 and must not be merged or closed without
  explicit owner authorization.

## Risks

- Real macOS authorization, driver behavior, network policy, and restoration
  remain operator and platform concerns outside mocked validation.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and verification.
