# Partial Mutation Error Boundary

status: completed

## Summary

Report when a live command sequence fails after the interface address mutation
has already succeeded, without attempting automatic restoration or exposing
interface and address identifiers.

## Problem

`set_mac_address` runs four privileged commands in sequence. If the final
hardware refresh fails after the `ifconfig ... ether` command succeeds, the
caller receives only the generic command failure even though the interface may
already hold the requested address. That obscures the operator's required
verification and restoration decision.

## Requirements

- Distinguish failures before address mutation from failures after mutation.
- Preserve the original sanitized command failure before mutation.
- Raise an identifier-free partial-state error after the address command has
  succeeded and any later command fails.
- Chain no sensitive subprocess diagnostics into the public error.
- Perform no automatic restoration, persistence, interface enumeration, or
  additional privileged mutation.
- Preserve dry-run behavior and successful post-change verification.

## Implementation

- Track completion of the exact `ifconfig <interface> ether <address>` command
  while executing the existing command list.
- Wrap only the live command loop and translate later failures into a stable
  partial-mutation error with the original exception suppressed.
- Add mocked tests for failures before and after mutation and static ordering,
  sanitization, documentation, and completed-plan contracts.

## Verification

- Run the focused mocked unit suite and every Make gate from repository and
  external working directories.
- Reject mutations that remove state tracking, misclassify pre-mutation
  failures, leak identifiers, add rollback behavior, remove tests or guidance,
  or leave plan evidence incomplete.
- Audit exact diff, generated artifacts, conflict markers, binary/large files,
  and changed-line credential or captured-identifier patterns.

## Risks

- The utility cannot prove final network state when refresh fails; the error
  deliberately requires operator inspection under the existing restoration
  runbook.
- Real privileged macOS networking commands remain outside Linux-hosted tests.
- The change must remain stacked on PR #9 and must not be merged or closed
  without explicit owner authorization.

## Work Completed

- Tracked successful completion of the exact interface address command inside
  the existing live command loop.
- Preserved original failures before mutation and translated later failures to
  an identifier-free partial-state error with exception chaining suppressed.
- Added mocked pre/post-boundary regressions, ordering contracts, and operator,
  security, vision, and change-history guidance without automatic rollback.

## Verification Completed

- All 20 mocked, non-privileged unit tests passed.
- `make lint`, `make test`, `make build`, `make verify`, `make check`, and the
  external working directory gate passed.
- Python source compilation, shell syntax, workflow YAML, legacy plist, and XML
  documentation checks passed without invoking macOS networking commands.
- Six isolated hostile mutations removing mutation tracking, marking state too
  early, removing translation, leaking identifiers, deleting guidance, or
  reverting completed plan status were rejected.
- `git diff --check`, exact-diff, generated-artifact, conflict-marker,
  intended-path, binary/large-file, changed-line credential, and captured
  identifier audits passed.
