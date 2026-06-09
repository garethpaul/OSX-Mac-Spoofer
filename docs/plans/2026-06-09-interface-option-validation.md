---
status: completed
date: 2026-06-09
---

# Interface Option Validation

## Context

`SpoofMACAddress.py` already builds platform commands as argument lists and
rejects shell metacharacters in interface names. A remaining boundary was
option-like interface input such as `--help`: it is not shell injection, but it
can still be interpreted by command-line tools as an option rather than as an
interface value.

## Objectives

- Reject interface names that start with a dash before command construction.
- Keep valid macOS-style interface names such as `en0` unchanged.
- Cover the behavior with no-network unit tests and the static baseline check.
- Document the guardrail in the README, security policy, and project vision.

## Verification

- `make check`
- `git diff --check`
