# Bytecode-Free Verification

status: completed

## Context

The static verification target used `python3 -m py_compile`, which writes
`.pyc` files as part of the check. This left ignored `__pycache__` output after
normal local verification even though the repository treats those files as
generated tooling artifacts.

## Objectives

- Replace `py_compile` with a bytecode-free syntax compile.
- Run unittest discovery and the static checker with bytecode writes disabled.
- Add a baseline guard for leftover `__pycache__` and `.pyc` output.
- Keep shell syntax checks and no-network tests unchanged.
- Document Python bytecode as local tooling output.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
