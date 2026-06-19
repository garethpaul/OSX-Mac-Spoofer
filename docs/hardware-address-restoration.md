# Hardware Address Restoration

Review date: 2026-06-13

This runbook is for an authorized operator restoring one known macOS network
interface after an explicit spoofing change. It does not add an automatic
restore mode, persistence, broad interface discovery, or a way to bypass local
network policy.

## Address Roles

- The **current address** is what `ifconfig` reports for the active interface.
- The **hardware address** is what `networksetup -getmacaddress` reports for the
  selected interface.
- A **spoof target** accepted by this utility must be a nonzero, locally
  administered unicast address. A legitimate hardware address is commonly
  globally administered, so it is intentionally not accepted as a normal
  spoof target.

Do not commit or paste real interface inventories, hardware addresses, host
names, network names, or authorization records into this repository, issues,
logs, screenshots, or test fixtures.

## Before A Change

Confirm the interface and maintenance authorization with the device or network
owner. Record the following in an approved private operational record:

- interface name
- current address
- hardware address
- maintenance window and operator
- expected connectivity and network-access checks

Use read-only discovery commands and review their output locally:

```bash
INTERFACE=en0
networksetup -getmacaddress "$INTERFACE"
ifconfig "$INTERFACE" | awk '/ether/{print $2; exit}'
```

Before applying a spoof target, review the utility's exact command sequence:

```bash
python3 SpoofMACAddress.py "$INTERFACE" 02:23:45:67:89:ab --dry-run
```

Dry-run mode must remain subprocess-free and does not verify privileges,
interface availability, connectivity, or network policy.

## Restore The Recorded Hardware Address

Stop traffic that depends on the interface and confirm the recorded values
again. Set `HARDWARE_ADDRESS` only to the exact address captured for the same
interface before the spoofing change:

```bash
INTERFACE=en0
HARDWARE_ADDRESS=aa:bb:cc:dd:ee:ff
printf 'interface=%s restore-address=%s\n' "$INTERFACE" "$HARDWARE_ADDRESS"
sudo ifconfig "$INTERFACE" ether "$HARDWARE_ADDRESS"
networksetup -detectnewhardware
```

The direct `ifconfig` command is intentionally separate from
`SpoofMACAddress.py`: the utility's spoof-target validator must continue to
reject globally administered addresses. Do not weaken that validator or use an
address copied from another device.

## Verify Recovery

Re-run both read-only views:

```bash
networksetup -getmacaddress "$INTERFACE"
ifconfig "$INTERFACE" | awk '/ether/{print $2; exit}'
```

Confirm all of the following before ending the maintenance window:

- the current address matches the recorded hardware address
- the hardware view still matches the pre-change record
- expected local connectivity is restored
- applicable access-control, inventory, and network-policy checks pass
- no startup wrapper or other automation is configured to reapply a spoofed
  address

## Failure And Escalation

Stop rather than trying unrelated interfaces or addresses when discovery and
current-state output disagree. Interface names, required privileges, private
address behavior, managed-device controls, and network enforcement vary by
platform and environment. Use the device owner's approved macOS and network
operations procedure, and reboot or cycle interface state only when that
procedure authorizes it.

Never add automatic startup restoration, hidden persistence, remote control,
broad interface enumeration, or network-policy evasion to resolve a failed
manual restoration.
