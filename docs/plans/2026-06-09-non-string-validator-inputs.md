# Non-String Validator Inputs Plan

status: completed

## Context

The MAC address and interface validators assumed string inputs and called
`.strip()` directly. Programmatic callers that passed `None`, bytes, or numeric
values could receive `AttributeError` instead of the same validation failure
used for malformed strings.

## Objectives

- Make MAC address normalization reject non-string values with `ValueError`.
- Make interface validation reject non-string values with `ValueError`.
- Add no-network unit tests for non-string MAC address and interface inputs.
- Extend static checks and docs so command construction remains guarded by
  explicit validation.

## Verification

- `python3 -m unittest discover -v`
- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
