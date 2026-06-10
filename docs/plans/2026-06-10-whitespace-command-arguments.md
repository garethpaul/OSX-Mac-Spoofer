# Whitespace Command Arguments

status: completed

## Context

`normalize_command` rejected empty command arguments, but direct callers could
still pass whitespace-only strings. Those values are misleading in dry-run
output and should not reach subprocess execution.

## Objectives

- Reject whitespace-only command arguments before rendering or execution.
- Preserve valid structured command argument lists.
- Extend no-network tests, docs, and the static baseline for whitespace-only
  command arguments.

## Verification

- `make test`
- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
