# Malformed Command Validation Plan

status: completed

## Context

`execute` and `command_text` were only called by internal argument-list builders,
but direct calls with malformed command sequences could still render empty
dry-run lines, split string commands into characters, or leak lower-level type
errors.

## Objectives

- Add `normalize_command` to validate subprocess command arguments before
  dry-run rendering or execution.
- Reject string, bytes, empty, and non-text command argument sequences with
  `ValueError`.
- Add no-network unit coverage for malformed command sequences.
- Extend static checks and docs for command execution validation.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
