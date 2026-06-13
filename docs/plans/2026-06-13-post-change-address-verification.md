# Post-Change Address Verification

status: completed

## Context

The live command path reads the interface address after running macOS network
commands but always prints a success message, even when the observed address
does not match the validated target.

## Requirements

- Compare the normalized post-command address with the normalized requested
  address before reporting success.
- Raise a concise error when the interface did not adopt the requested address.
- Do not expose command output, interface names, or MAC addresses in the error.
- Preserve dry-run isolation and add mocked, mutation-sensitive regression
  coverage without executing privileged commands.

## Scope Boundaries

- Do not change command order, defaults, validation, restoration guidance,
  launch behavior, dependencies, or timeout handling.

## Work Completed

- Added a normalized post-command equality check before hardware-address lookup
  and success output.
- Added a fully mocked live-path regression test that forces a mismatch, proves
  all four intended commands ran, prevents the follow-up hardware query, and
  verifies the error omits interface and MAC identifiers.
- Added current operator/security guidance plus ordering-sensitive source,
  test, documentation, and completed-plan contracts.

## Verification Completed

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_spoof_mac_address.py`
- `make lint`, `make test`, `make build`, `make verify`, and `make check`
- Ran the baseline checker from an external working directory.
- Parsed the workflow YAML and passed the legacy `StartupParameters.plist`
  static contract.
- Confirmed focused hostile mutations to comparison ordering, test assertions,
  current documentation, and completed-plan evidence are rejected.
- `git diff --check`
- The intended-path secret and generated-artifact scan passed; no privileged
  command ran, and command order, defaults, launch behavior, restoration
  guidance, dependencies, and timeout handling had no unrelated diff.
