# Python C2 Lab Simulator v2.1.0

Version 2.1.0 hardens the local controller/agent lab while preserving its deliberate loopback-only, no-shell security boundary.

## Highlights

- Protocol v2 with session IDs and correlated request IDs
- Strict frame, JSON, metadata, capability, and response validation
- Two-sided command allowlisting with no arbitrary shell fallback
- 64 KiB frame limit and bounded command/echo input
- Graceful interruption and handshake/connect timeouts
- Expanded unit and integration test coverage
- Ruff lint and formatting checks in CI
- Python 3.11, 3.12, and 3.13 CI matrix
- Automated branch-coverage quality gate with downloadable HTML report
- New protocol and security documentation
- Terminal demo preview plus asciinema-compatible recording

## Security boundary

The simulator remains intentionally constrained:

- controller binds only to `127.0.0.1`
- agent connects only to `127.0.0.1`
- no arbitrary OS command execution
- no `subprocess` execution path
- no persistence
- no credential collection
- no file transfer
- no remote deployment
- no exploitation
- no stealth/evasion features

## Upgrade notes

Protocol v2 is intentionally incompatible with the earlier protocol v1 message format. Controller and agent should be upgraded together.

## Validation

The repository CI validates:

- Ruff lint
- Ruff formatting
- compile checks
- unit/integration tests on Python 3.11, 3.12, and 3.13
- branch coverage against the configured quality gate

## Suggested GitHub release metadata

**Tag:** `v2.1.0`  
**Title:** `Python C2 Lab Simulator v2.1.0`  
**Target:** `main`

Use the sections above as the GitHub Release body.
