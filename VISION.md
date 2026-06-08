## OSX Mac Spoofer Vision

OSX Mac Spoofer is a legacy Python utility for changing a macOS network
interface MAC address using system networking commands.

The repository is useful as a small historical example of shelling out to
`networksetup`, `airport`, and `ifconfig` to inspect and update network
interface state.

The goal is to preserve the script as an explicit administrative tool while
making platform assumptions, permissions, and responsible-use boundaries clear.

The current focus is:

Priority:

- Keep interface and address changes visible to the operator
- Document supported macOS assumptions and required privileges
- Avoid background or automatic network changes
- Preserve the ability to pass an interface and address explicitly

Next priorities:

- Add README usage notes and a dry-run mode
- Update Python 2 syntax if the script is modernized
- Validate MAC address input before calling system commands
- Document how to restore hardware addresses

Contribution rules:

- One PR = one focused validation, platform, command, or documentation change.
- Do not add persistence without prominent user confirmation.
- Keep command execution auditable.
- Include manual verification notes for macOS changes.

## Security And Responsible Use

Changing network identifiers can affect access controls, logs, and network
policy. This utility should remain an explicit local admin tool and should not
be packaged for covert or automatic use.

## What We Will Not Merge (For Now)

- Background daemons that change addresses without consent
- Network evasion features
- Hidden persistence or launch agents
- Remote-control behavior
