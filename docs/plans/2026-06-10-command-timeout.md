# Bounded Command Timeout

status: completed

## Context

Validated argument lists prevent shell injection, but `subprocess.run` had no
deadline. A stalled `networksetup`, `airport`, or `ifconfig` process could hang
the utility or startup wrapper indefinitely.

## Objectives

- Apply a 15-second timeout to every executed platform command.
- Convert `TimeoutExpired` into a clear `RuntimeError`.
- Identify only the executable in timeout errors, omitting interface and MAC
  arguments.
- Preserve dry-run behavior without launching subprocesses.
- Extend mocked tests, docs, and static checks for the timeout contract.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- `git diff --check`
