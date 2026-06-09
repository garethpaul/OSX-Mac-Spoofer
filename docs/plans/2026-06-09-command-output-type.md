# Command Output Type Plan

status: completed

## Context

`parse_mac_address` extracts observed MAC addresses from command output after
`execute` returns text. Direct calls with non-string output could still raise a
raw regular-expression type error before reaching the normal `ValueError`
validation path.

## Objectives

- Reject non-string command output before searching for observed MAC addresses.
- Preserve existing observed hardware MAC normalization.
- Add unit coverage for non-string parser output values.
- Extend static checks and docs so the parser boundary remains explicit.

## Verification

- `python3 -m unittest discover -v`
- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
