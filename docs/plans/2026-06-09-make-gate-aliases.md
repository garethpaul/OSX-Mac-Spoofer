# Make Gate Aliases Plan

status: completed

## Context

`OSX-Mac-Spoofer` already had a `make check` target for no-network unit tests,
Python compilation, shell syntax checks, and static baseline verification. The
shared maintenance workflow also expects common aliases for linting, building,
and full verification.

## Objectives

- Add `make lint` as the static Python, shell, and baseline-check alias.
- Add `make build` as the no-network build-through-test alias.
- Add `make verify` as the full verification alias.
- Extend docs and baseline checks so the aliases remain discoverable.

## Verification

- `make lint`
- `make build`
- `make verify`
- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
