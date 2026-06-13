# Post-Change Address Verification

status: pending

## Context

The live command path reads the interface address after running macOS network
commands but always prints a success message, even when the observed address
does not match the validated target.

## Requirements

- Compare the normalized post-command address with the normalized requested
  address before reporting success.
- Raise a concise error when the interface did not adopt the requested address.
- Do not expose command output, interface names, or MAC addresses in the error.
- Preserve dry-run isolation and add mocked, mutation-sensitive regression
  coverage without executing privileged commands.

## Scope Boundaries

- Do not change command order, defaults, validation, restoration guidance,
  launch behavior, dependencies, or timeout handling.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation.
