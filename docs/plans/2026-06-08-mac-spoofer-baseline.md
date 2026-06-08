# OSX Mac Spoofer Baseline Plan

status: completed

## Context

`OSX-Mac-Spoofer` is a legacy macOS utility that changes a local network
interface MAC address using `networksetup`, `airport`, and `ifconfig`.

## Risks

- The original Python 2 script used shell-string command execution.
- MAC address and interface values were not validated before command execution.
- The startup wrapper implied automatic execution without an explicit apply
  gate.
- There was no no-network test path for command construction or dry-run
  behavior.

## Work Completed

- Ported the utility to Python 3 and added argument parsing.
- Added MAC address normalization, interface validation, dry-run command output,
  and structured subprocess calls.
- Made the startup wrapper run dry-run by default unless
  `SPOOF_MAC_ADDRESS_APPLY=1` is set.
- Added unit tests for validation, command construction, and dry-run behavior.
- Replaced legacy multicast default addresses with unicast defaults and reject
  multicast MAC address input.
- Added `make check` and `scripts/check-baseline.py` for repeatable local
  verification.
- Updated README, security, vision, changelog, and ignore rules.

## Verification

- `make check`
- `python3 -m unittest discover -v`
- `python3 scripts/check-baseline.py`
- `git diff --check`
