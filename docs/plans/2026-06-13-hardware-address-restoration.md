# Hardware Address Restoration Guidance

status: completed

## Context

The utility reports current and hardware addresses after a live change, but it
does not document how an operator should record the original address, restore
it deliberately, verify recovery, or respond when interface state and hardware
reporting disagree. The spoof-target validator intentionally requires locally
administered addresses, so hardware restoration must not be presented as a
normal spoof-target invocation.

## Priorities

1. Require operators to capture interface and hardware identity before change.
2. Document an explicit, reviewable restoration procedure without adding
   persistence or weakening spoof-target validation.
3. Define verification, failure, and escalation boundaries for network-policy
   and platform-specific behavior.

## Requirements

- R1. Explain the distinction between the observed current address, hardware
  address, and locally administered spoof target.
- R2. Require pre-change capture of interface name, current address, hardware
  address, and the authorized maintenance context without committing machine
  identifiers to the repository.
- R3. Show read-only discovery commands and a direct explicit restoration
  command whose interface and hardware address are reviewed before execution.
- R4. Require dry-run review of the utility's disconnect/change/refresh command
  sequence before any spoofing operation.
- R5. Define post-restore checks using both current and hardware address views,
  connectivity, and applicable network access policy.
- R6. State that interface names, permissions, private-address behavior, and
  network controls are platform and environment dependent.
- R7. Prohibit automatic startup restoration, hidden persistence, broad
  interface enumeration, captured identifiers, and claims that restoration
  bypasses network policy.
- R8. Enforce the guidance and completed evidence through the existing static
  baseline without changing Python, shell wrapper, plist, or command behavior.

## Implementation Units

### U1: Restoration Runbook

File: `docs/hardware-address-restoration.md`

Document pre-change capture, dry-run review, explicit restore, verification,
failure handling, privacy boundaries, and residual platform uncertainty.

### U2: Guidance Integration

Files: `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`

Link the runbook from operator, security, and maintenance guidance and move the
restoration backlog item into the maintained priority contract.

### U3: Static Contract And Evidence

Files: `scripts/check-baseline.py`,
`docs/plans/2026-06-13-hardware-address-restoration.md`

Require the runbook's safety boundaries, unchanged implementation surfaces,
completed plan status, and truthful verification evidence.

## Verification Plan

- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- run the checker from an external working directory
- parse workflow YAML and statically verify the legacy OpenStep plist contract
- run focused hostile mutations against restoration safety boundaries
- verify `SpoofMACAddress.py`, `SpoofMACAddress`, `StartupParameters.plist`, and
  tests have no diff
- `git diff --check`
- scan intended paths for secrets, captured identifiers, and generated artifacts

## Scope Boundaries

- Do not execute or add privileged commands, restore modes, background jobs,
  launch agents, persistence, interface enumeration, or platform probes.
- Do not weaken locally administered spoof-target validation.
- Do not claim one procedure works on every macOS release, interface type,
  managed device, or network.

## Work Completed

Added a restoration runbook covering private pre-change capture, address-role
boundaries, dry-run review, explicit direct restoration, state/connectivity
verification, and failure escalation without changing command behavior.

## Verification Completed

- `make lint`, `make test`, `make build`, `make verify`, and `make check`
  passed.
- The checker passed from an external working directory; workflow YAML parsed
  successfully, and the legacy `StartupParameters.plist` static contract was
  verified.
- Ten focused hostile mutations rejected weakened capture, validator,
  verification, anti-persistence, and completed-plan requirements.
- `implementation and test paths had no diff`, including `SpoofMACAddress.py`,
  `SpoofMACAddress`, `StartupParameters.plist`, and `test_spoof_mac_address.py`.
- `git diff --check` passed.
- The `secret, captured-identifier, and generated-artifact scan` passed.
