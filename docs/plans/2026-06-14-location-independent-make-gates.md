# Location-Independent Make Gates

status: planned

## Context

The standard Make aliases pass from the repository root, but an absolute
Makefile invocation from another directory resolves unittest discovery,
source compilation, shell syntax validation, and the baseline checker against
the caller. Shared automation should run the same mocked, non-privileged gate
without changing its own working directory.

## Requirements

- Derive an override-protected repository root from the Makefile location.
- Give unittest discovery an explicit rooted start directory without changing
  Python override semantics, verbosity, selection, or bytecode suppression.
- Compile each existing Python source by rooted path while retaining useful
  repository-relative filenames in syntax errors.
- Run shell syntax and the Python baseline checker by rooted path.
- Preserve the current alias graph, sixteen mocked tests, anti-automation
  policy, runtime code, plist contract, workflow matrix, and no-privilege rule.
- Statically reject caller-relative or caller-overridable gate execution.

## Scope Boundaries

- Do not run `sudo`, `ifconfig`, `networksetup`, `airport`, or real interface
  mutation and inspection commands.
- Do not change MAC validation, command ordering, timeout, sanitization,
  restoration guidance, dependencies, runtime code, tests, or workflow jobs.
- Do not weaken the baseline checker or mocked test suite.

## Implementation Units

1. Root unittest, Python compilation, shell syntax, and checker execution while
   preserving every existing alias and command option.
2. Extend `scripts/check-baseline.py` to require rooted recipes, this plan,
   completed evidence, and maintenance documentation.
3. Document the external invocation contract in `README.md` and `CHANGES.md`.

## Verification Plan

- Run all standard aliases from the repository root and through the absolute
  Makefile path from `/tmp`.
- Confirm caller-supplied repository-root and relative Python variables cannot
  redirect paths or reinterpret the selected interpreter.
- Parse workflow YAML, compile the checker outside the repository, validate
  shell syntax and the legacy plist, and run focused mocked tests.
- Run isolated hostile mutations over each rooted command and plan evidence.
- Audit intended paths, unchanged runtime/tests, generated artifacts, captured
  identifiers, and secret-like data.
