#!/usr/bin/env python3
"""Change a macOS network interface MAC address with explicit validation."""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
import argparse
from typing import Iterable, List, Optional, Sequence, Tuple


DEFAULT_WIRELESS_ADDRESS = "01:23:45:67:89:ab"
DEFAULT_WIRED_ADDRESS = "cd:ef:12:34:56:78"

# Path to Airport binary differs between OS X releases. This is the 10.7 path.
PATH_TO_AIRPORT = "/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport"

MAC_ADDRESS_RE = re.compile(
    r"^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$|^[0-9a-fA-F]{12}$"
)
INTERFACE_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")
MAC_IN_OUTPUT_RE = re.compile(r"\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b")


def normalize_mac_address(address: str) -> str:
    """Return a colon-separated lower-case MAC address."""

    candidate = address.strip()
    if not MAC_ADDRESS_RE.match(candidate):
        raise ValueError(
            "MAC address must be 12 hex characters or 6 colon-separated octets"
        )

    octets = candidate.replace(":", "").lower()
    return ":".join(octets[index : index + 2] for index in range(0, 12, 2))


def validate_interface(interface: str) -> str:
    """Validate an interface name before passing it to system commands."""

    candidate = interface.strip()
    if not candidate:
        raise ValueError("interface is required")
    if not INTERFACE_RE.match(candidate):
        raise ValueError("interface contains unsupported characters")
    return candidate


def parse_mac_address(output: str) -> str:
    """Extract the first colon-separated MAC address from command output."""

    match = MAC_IN_OUTPUT_RE.search(output)
    if not match:
        raise ValueError("no MAC address found in command output")
    return normalize_mac_address(match.group(0))


def command_text(command: Sequence[str]) -> str:
    return shlex.join(command)


def execute(command: Sequence[str], *, dry_run: bool = False) -> str:
    """Run a command and return stdout, or print it when dry-running."""

    if dry_run:
        print(f"+ {command_text(command)}")
        return ""

    result = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        raise RuntimeError(f"{command[0]} failed: {detail}")
    return result.stdout


def get_mac_address(interface: str, *, hardware: bool = False) -> str:
    """Return the current or hardware MAC address for an interface."""

    checked_interface = validate_interface(interface)
    if hardware:
        output = execute(["networksetup", "-getmacaddress", checked_interface])
    else:
        output = execute(["ifconfig", checked_interface])
    return parse_mac_address(output)


def change_commands(
    interface: str, address: str, *, airport_interface: str
) -> List[List[str]]:
    """Build the commands needed to change and refresh the MAC address."""

    checked_interface = validate_interface(interface)
    checked_airport_interface = validate_interface(airport_interface)
    checked_address = normalize_mac_address(address)
    return [
        ["networksetup", "-setairportpower", checked_airport_interface, "on"],
        [PATH_TO_AIRPORT, "-z"],
        ["ifconfig", checked_interface, "ether", checked_address],
        ["networksetup", "-detectnewhardware"],
    ]


def set_mac_address(
    interface: str,
    address: str,
    *,
    airport_interface: str = "en1",
    dry_run: bool = False,
) -> None:
    """Change an interface MAC address using macOS networking commands."""

    checked_interface = validate_interface(interface)
    checked_address = normalize_mac_address(address)
    commands = change_commands(
        checked_interface, checked_address, airport_interface=airport_interface
    )

    if dry_run:
        print("Dry run: no network state will be changed.")
        for command in commands:
            execute(command, dry_run=True)
        return

    old_address = get_mac_address(checked_interface)

    for command in commands:
        execute(command)

    new_address = get_mac_address(checked_interface)
    hardware_address = get_mac_address(checked_interface, hardware=True)
    print(
        "Changed {} (h/w: {}) from {} to {}.".format(
            checked_interface, hardware_address, old_address, new_address
        )
    )
    print(
        "If both addresses are the same, run 'ifconfig {} | grep ether' in a few seconds.".format(
            checked_interface
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Change a macOS network interface MAC address."
    )
    parser.add_argument("interface", nargs="?", help="interface to update, for example en0")
    parser.add_argument(
        "address",
        nargs="?",
        help="MAC address as 12 hex characters or colon-separated octets",
    )
    parser.add_argument(
        "--airport-interface",
        default="en1",
        help="airport interface to disassociate before changing the address",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print commands without changing network state",
    )
    return parser


def resolve_target(args: argparse.Namespace) -> Tuple[str, str, str]:
    values = [args.interface, args.address]
    if all(value is None for value in values):
        print("Using default MAC address for en0.")
        return "en0", DEFAULT_WIRED_ADDRESS, args.airport_interface
    if any(value is None for value in values):
        raise ValueError("provide both interface and address, or neither")

    print("Using manual MAC address.")
    return args.interface, args.address, args.airport_interface


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        interface, address, airport_interface = resolve_target(args)
        set_mac_address(
            interface,
            address,
            airport_interface=airport_interface,
            dry_run=args.dry_run,
        )
    except ValueError as error:
        parser.error(str(error))
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
