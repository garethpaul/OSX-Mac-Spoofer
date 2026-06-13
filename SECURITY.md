# Security Policy

## Supported Versions

The supported security scope for `OSX-Mac-Spoofer` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Spoof your MAC address

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/OSX-Mac-Spoofer` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a public sample, documentation, or utility project. The active security scope is the code and documentation on the default branch.
- Review found shell execution, subprocess, or dynamic evaluation surfaces; changes in those areas should receive security-focused review before merge.
- The active script changes local macOS network interface state through
  `networksetup`, `airport`, and `ifconfig`. Treat command construction,
  argument validation, and startup behavior as security-sensitive.
- The startup wrapper runs dry-run mode unless `SPOOF_MAC_ADDRESS_APPLY=1` is
  set. Do not add background or persistent address changes without prominent
  operator consent.
- MAC address inputs should stay constrained to nonzero, locally administered
  unicast values before command construction.
- Interface names that start with a dash should stay rejected so operator
  input cannot be interpreted as extra platform-tool options.
- Observed current or hardware MAC addresses from macOS command output should
  be normalized without requiring the local-admin bit, because hardware
  addresses are commonly globally administered.
- Hardware restoration must use the exact interface and address captured in an
  approved private operational record before a change. Do not weaken locally
  administered spoof-target validation, copy another device's address,
  enumerate unrelated interfaces, or store captured identifiers in repository
  artifacts.
- Non-string MAC address and interface values should fail validation before any
  command arguments are built.
- Non-string command output should fail validation before observed MAC parsing.
- Malformed command sequences should fail validation before dry-run rendering
  or subprocess execution.
- Whitespace-only command arguments should fail validation before dry-run
  rendering or subprocess execution.
- A bounded command timeout should prevent stalled platform tools from hanging
  the utility, and timeout errors should not expose command arguments.
- Nonzero command failures should report only the executable and exit status;
  captured standard output, standard error, and command arguments may contain
  host-specific details and should not be repeated.
- Post-change verification should require the observed address to match the
  requested target and report mismatches without interface or MAC identifiers.
- Python bytecode is local tooling output and should not remain after
  verification gates.
- Pinned, read-only hosted Linux validation runs only mocked command tests and
  shell syntax checks; it must never invoke privileged network changes.
- Hosted verification uses a credential-free checkout so its read-only token is
  not retained in the runner's Git configuration.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.


## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

Do not commit network captures, interface inventories, local machine names, or
organization-specific MAC addresses. Run `make lint`, `make build`,
`make verify`, and `make check` before changing command execution, argument
validation, or service-wrapper behavior.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
