# Changes

## 2026-06-08

- Ported `SpoofMACAddress.py` to Python 3 with argument parsing, MAC address
  normalization, interface validation, and dry-run support.
- Removed shell-string command execution in favor of argument-list subprocess
  calls.
- Updated the startup wrapper to dry-run by default unless
  `SPOOF_MAC_ADDRESS_APPLY=1` is set.
- Added no-network unit tests, `make check`, and static baseline verification.
- Documented responsible-use boundaries and local admin requirements.
- Updated default addresses and validation to reject multicast MAC addresses.
- Rejected the all-zero MAC address before command construction.
- Required spoofed MAC addresses to be locally administered unicast addresses.
