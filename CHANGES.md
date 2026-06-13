# Changes

## 2026-06-13

- Verify the observed post-command interface address matches the requested
  target before reporting a successful change.
- Added an explicit hardware-address restoration runbook covering private
  pre-change capture, dry-run review, direct restoration, state/connectivity
  verification, failure escalation, and anti-persistence boundaries.

## 2026-06-12

- Disabled persisted checkout credentials and enforced the sole pinned
  credential-free workflow boundary.
- Sanitized nonzero platform-command failures so errors report only the
  executable and exit status, without captured output or command arguments.

## 2026-06-09

- Rejected malformed command sequences before dry-run rendering or subprocess
  execution.
- Added stable Make aliases for lint, build-through-test, and full verification
  gates.
- Made verification bytecode-free and added a guard against leftover Python
  bytecode.

## 2026-06-10

- Added pinned, read-only hosted Linux validation on Python 3.10 and 3.12 for
  the mocked, non-privileged command baseline.
- Rejected whitespace-only command arguments before dry-run rendering or
  subprocess execution.
- Added a 15-second command timeout with sanitized timeout errors that omit
  interface and MAC arguments.

## 2026-06-08

- Ported `SpoofMACAddress.py` to Python 3 with argument parsing, MAC address
  normalization, interface validation, and dry-run support.
- Removed shell-string command execution in favor of argument-list subprocess
  calls.
- Updated the startup wrapper to dry-run by default unless
  `SPOOF_MAC_ADDRESS_APPLY=1` is set.
- Added no-network unit tests, `make check`, and static baseline verification.
- Documented responsible-use boundaries and local admin requirements.
- Updated default addresses and validation to reject multicast MAC addresses.
- Rejected the all-zero MAC address before command construction.
- Required spoofed MAC addresses to be locally administered unicast addresses.
- Split observed MAC address normalization from spoof-target validation so
  globally administered hardware addresses can still be reported.
- Rejected option-like interface names that start with a dash before command
  construction.
- Rejected non-string MAC address and interface values before normalization or
  command construction.
- Rejected non-string command output before observed MAC address parsing.
