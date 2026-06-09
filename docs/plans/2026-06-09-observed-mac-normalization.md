# Observed MAC Normalization Plan

status: completed

## Context

Spoof targets must be locally administered addresses, but current or hardware
MAC addresses read from `ifconfig` and `networksetup` are often globally
administered. Reusing the spoof-target validator for observed command output
could fail before or after a legitimate local change.

## Objectives

- Keep spoof target validation constrained to nonzero locally administered
  unicast addresses.
- Add `normalize_observed_mac_address` for command output parsing where
  globally administered unicast hardware addresses are valid.
- Keep malformed, all-zero, and multicast observed values rejected.
- Extend no-network tests and static baseline coverage for the split.

## Verification

- `python3 -m unittest discover -v`
- `make check`
- `python3 -m py_compile SpoofMACAddress.py test_spoof_mac_address.py scripts/check-baseline.py`
- `sh -n SpoofMACAddress`
- `python3 scripts/check-baseline.py`
- `git diff --check`
