# Mutation Command Error Boundary

status: completed

## Context

The partial-state guard activates only after the address command returns
successfully. If `ifconfig ... ether ...` applies the change and then times out
or exits nonzero, the utility reports an ordinary pre-mutation failure even
though network state may already have changed.

## Goal

Treat failure of the mutation command itself as an ambiguous partial state that
requires manual inspection and restoration, while preserving failures from
commands that run before mutation.

## Scope

- Route an exception from the exact address command through the sanitized
  partial-state message.
- Preserve original pre-mutation exceptions and post-mutation behavior.
- Add mocked regression coverage, static ordering contracts, synchronized
  guidance, and completed verification evidence.
- Do not execute privileged commands, automatically roll back, or expose
  interface/address identifiers.

## Verification Plan

- Run the mocked unit suite and all Make gates from repository and external
  directories on Python 3.10 and 3.12 where available.
- Reject isolated command-identity, exception-boundary, test, guidance, and plan
  mutations.
- Run `git diff --check` and audit bytecode, dependency files, binaries, modes,
  credentials, and intended paths.

## Work Completed

- Extended the partial-state boundary to cover failure of the exact address
  mutation command as well as later command failures.
- Preserved original exceptions from commands that run before the mutation
  attempt.
- Added a mocked regression for the ambiguous mutation-command result, static
  source and test contracts, synchronized operator guidance, and this completed
  evidence record.

## Verification Completed

- All 21 mocked, non-privileged unit tests passed on the available local Python
  3.12 runtime; the three focused pre-mutation, mutation-command, and
  post-mutation error-boundary tests also passed independently.
- `make lint`, `make test`, `make build`, `make verify`, and `make check` passed
  with Python 3.12 from both the repository and an external working directory.
- Five isolated hostile mutations were rejected: deleting the new runtime
  branch, inverting command identity, removing the regression contract,
  removing synchronized guidance, and reverting plan completion.
- `git diff --check` passed, and the explicit secret and generated-artifact scan
  found no credential patterns, `__pycache__` directories, or `.pyc` files in
  the intended change.
