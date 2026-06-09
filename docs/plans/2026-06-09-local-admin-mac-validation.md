# Local Admin MAC Validation Plan

status: completed

## Context

The MAC validator rejected multicast and all-zero addresses, but still accepted
globally administered unicast addresses. A spoofing helper should prefer
locally administered addresses so users do not accidentally claim vendor-owned
address space.

## Objectives

- Reject MAC addresses without the locally administered bit set.
- Keep the existing compact and colon-separated address formats.
- Extend tests, docs, and the static checker for the validation rule.

## Verification

- `python3 -m unittest discover -v`
- `make check`
- `python3 -m py_compile SpoofMACAddress.py test_spoof_mac_address.py scripts/check-baseline.py`
- `sh -n SpoofMACAddress`
- `python3 scripts/check-baseline.py`
- `git diff --check`
