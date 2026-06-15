# Mutation Command Error Boundary

status: in_progress

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

Pending implementation.

## Verification Completed

Pending implementation and validation.
