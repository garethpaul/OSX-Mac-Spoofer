# Startup Script Path Boundary

Status: completed

## Problem

The legacy `/etc/rc.common` wrapper may run with administrative privileges but
accepted `SPOOF_MAC_ADDRESS_SCRIPT` as an arbitrary Python path. The override
was undocumented and unused by the maintained tests, and dry-run mode could not
make attacker-selected Python safe because the selected script executes before
the utility can enforce its own network boundary.

## Design

- Bind `SCRIPT_PATH` to `SpoofMACAddress.py` adjacent to the wrapper.
- Preserve `SPOOF_MAC_ADDRESS_APPLY=1` as the explicit live-change opt-in.
- Preserve dry-run as the default startup behavior.
- Add a focused regression and static baseline that reject
  `SPOOF_MAC_ADDRESS_SCRIPT`.

## Alternatives

- Allowlisting paths beneath the repository remains vulnerable to writable
  replacements and symlink races and adds complexity for an unused feature.
- Allowing overrides only during dry-run still executes arbitrary Python under
  the wrapper's privilege before any dry-run guarantee can apply.
- Validating ownership and permissions at runtime duplicates platform policy
  without a product requirement for script replacement.

## Scope Boundaries

- Do not change MAC validation, network command ordering, apply consent,
  restoration guidance, platform paths, or launch service metadata.

## Work Completed

- Removed the arbitrary Python path override from the startup wrapper.
- Added `test_startup_wrapper_binds_the_checked_in_python_script` and baseline
  contracts for the fixed adjacent path.
- Updated security, roadmap, changelog, and completed plan guidance.

## Verification Completed

- The focused regression failed before implementation because
  `SPOOF_MAC_ADDRESS_SCRIPT` remained in the wrapper.
- All 28 mocked unit tests pass after implementation.
- `make check`, `make lint`, `make build`, and `make verify` pass both from the
  repository and through an absolute Makefile path outside the repository.
- Shell syntax, Python compilation, static baseline checks, and all four
  adversarial Makefile-root tests pass.
- Restoring the arbitrary `SPOOF_MAC_ADDRESS_SCRIPT` fallback makes
  `test_startup_wrapper_binds_the_checked_in_python_script` fail.
