# Nonzero MAC Validation

status: completed

## Context

The utility validates MAC address shape and rejects multicast addresses before
building command arguments. It still accepted `00:00:00:00:00:00`, which is not
a meaningful spoofed interface identifier.

## Objectives

- Preserve compact and colon-separated MAC address input support.
- Reject the all-zero MAC address before command construction.
- Keep multicast rejection and dry-run behavior intact.
- Extend no-network tests and static docs for nonzero unicast validation.

## Verification

- `make check`
- `python3 -m unittest discover -v`
- `python3 scripts/check-baseline.py`
- `git diff --check`
