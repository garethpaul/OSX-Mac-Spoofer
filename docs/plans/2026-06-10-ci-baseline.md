# CI Baseline

status: completed

## Context

The repository had local Python and shell verification gates for the MAC
spoofing utility, but no hosted workflow ran them for pushes and pull requests.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and runs
  `make check`.
- Extended the baseline checker and docs so the hosted CI path stays visible.

## Verification

- `make check`
