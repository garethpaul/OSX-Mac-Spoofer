# Hosted Safe Validation

status: completed

## Context

The utility changes macOS network interface state when run for real, but its
maintained tests mock command execution and require no privileges. There is no
hosted gate ensuring those validation and dry-run contracts remain portable.

## Priorities

1. Run the canonical mocked gate for pushes and pull requests.
2. Verify Python 3.10 and Python 3.12 behavior on fixed hosted Linux.
3. Pin actions, permissions, runner, timeout, and concurrency.
4. Keep CI non-privileged and free of actual interface changes.
5. Enforce the workflow contract from `scripts/check-baseline.py`.

## Implementation Units

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Add a commit-pinned, read-only Python matrix that runs `make check`. The gate
uses unit-test command mocks, Python compilation, and `sh -n`; it does not call
`sudo`, `ifconfig`, `networksetup`, or the macOS airport binary.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- Python 3.10 container `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted Linux `Check` workflow for both Python versions

## Boundaries

- Do not execute privileged network changes in CI.
- Do not change command behavior or default MAC addresses.
- Do not add dependencies in this pass.
