## OSX Mac Spoofer Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

OSX Mac Spoofer is a legacy Python utility for changing a macOS network
interface MAC address using system networking commands.

The repository is useful as a small historical example of shelling out to
`networksetup`, `airport`, and `ifconfig` to inspect and update network
interface state.

The goal is to preserve the script as an explicit administrative tool while
making platform assumptions, permissions, and responsible-use boundaries clear.

Current baseline: `make check` verifies parser, validation, and dry-run
behavior without touching the local network. `make lint`, `make build`, and
`make verify` provide stable aliases for static checks, build-through-test, and
full verification.

The current focus is:

Priority:

- Keep interface and address changes visible to the operator
- Document supported macOS assumptions and required privileges
- Prefer dry-run behavior before any network change
- Avoid background or automatic network changes
- Preserve the ability to pass an interface and address explicitly
- Keep MAC address validation limited to nonzero, locally administered unicast
  values
- Reject option-like interface names before command construction
- Keep observed hardware or current MAC address parsing separate from spoof
  target validation
- Keep non-string validator inputs out of command construction
- Keep non-string command output out of observed MAC parsing
- Reject malformed command sequences before dry-run rendering or subprocess
  execution
- Reject whitespace-only command arguments before dry-run rendering or
  subprocess execution
- Keep a bounded command timeout around every platform tool invocation
- Keep nonzero command errors free of captured output and command arguments
- Require the observed post-command address to match the requested target
  before reporting success
- Capture current and hardware addresses before mutation commands begin
- Surface post-mutation command failures as sanitized partial state requiring
  manual inspection and restoration
- Keep verification targets from leaving Python bytecode behind
- Keep Python 3.10 and 3.12 hosted Linux validation mocked and non-privileged
- Keep hosted source retrieval credential-free after checkout
- Keep `make lint`, `make build`, `make verify`, and `make check` available as
  local verification gates
- Keep hardware-address restoration explicit, privately recorded, manually
  verified, and separate from locally administered spoof-target validation

Next priorities:

- Add macOS manual verification notes for current supported versions
- Add more command argument validation fixtures for malformed direct calls
- Document local policy expectations for choosing spoofed nonzero unicast
  addresses
- Consider replacing the legacy `/etc/rc.common` wrapper with a clearly
  documented modern launchd example if startup behavior is still needed

Contribution rules:

- One PR = one focused validation, platform, command, or documentation change.
- Do not add persistence without prominent user confirmation.
- Keep command execution auditable.
- Keep `make lint`, `make build`, `make verify`, and `make check` passing for
  parser, validation, and dry-run changes.
- Preserve bytecode-free verification when changing Makefile gates.
- Include manual verification notes for macOS changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Changing network identifiers can affect access controls, logs, and network
policy. This utility should remain an explicit local admin tool and should not
be packaged for covert or automatic use.

## What We Will Not Merge (For Now)

- Background daemons that change addresses without consent
- Network evasion features
- Hidden persistence or launch agents
- Remote-control behavior

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
