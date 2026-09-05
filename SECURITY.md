# Security Policy

## Project boundary

This repository is intentionally a **loopback-only protocol simulator**.

The security boundary is part of the design:

- controller binds to `127.0.0.1`
- agent connects only to `127.0.0.1`
- no arbitrary shell execution
- no `subprocess` command execution
- no persistence
- no credential collection
- no file transfer
- no remote deployment
- no stealth/evasion features
- no exploitation features

Changes that remove these constraints should be treated as out of scope for this project.

## Supported version

Security fixes are applied to the latest code on the default branch.

## Reporting a vulnerability

Please open a GitHub issue for bugs that are safe to discuss publicly, such as malformed-frame handling, crashes, validation errors, or documentation inconsistencies.

For a report that could expose sensitive information, avoid posting secrets, credentials, private host data, or other confidential material in a public issue.

Useful reports should include:

- affected file/function
- Python version
- minimal reproduction steps
- expected behavior
- observed behavior
- whether the issue affects the loopback-only boundary

## Security goals

The project aims to:

1. fail closed on malformed protocol input;
2. bound message and command sizes;
3. correlate requests and responses;
4. keep the command vocabulary explicitly allowlisted;
5. preserve the loopback-only networking boundary;
6. avoid introducing OS command execution or remote-management functionality.
