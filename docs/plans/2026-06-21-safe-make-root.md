# Safe Make Root

## Problem

Whitespace-splitting Make functions and caller-controlled `MAKEFILE_LIST`
values could redirect mocked safety verification outside the checkout.

## Change

- Resolve the raw Makefile path with POSIX-compatible system tooling.
- Reject non-file origins for GNU Make's automatic `MAKEFILE_LIST` value.
- Shell-quote the resolved root once before any recipe uses it.
- Add dependency-free dry-run and live command-substitution regressions.

## Validation

- Run mocked tests, source compilation, shell syntax, static, and root gates.
- Confirm Python 3.10/3.12 and CodeQL pass at the exact pull-request head.
