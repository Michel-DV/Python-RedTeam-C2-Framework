# Changelog

All notable changes to the lab simulator are documented here.

## 2.1.0

### Added

- protocol v2 request/response correlation with `request_id`
- session identifiers in the handshake
- request IDs bound to the active session
- stricter agent metadata and capability validation
- controller-side command allowlist enforcement
- handshake/connect timeouts
- `--version` support for controller and agent
- Ruff lint/format configuration and CI checks
- controller handshake tests
- protocol documentation
- security policy

### Changed

- reduced the maximum protocol frame from 1 MiB to 64 KiB
- tightened command and echo input limits
- improved graceful interruption handling
- expanded tests for malformed frames, invalid request IDs, duplicate JSON keys, metadata validation, and command validation
- updated GitHub Actions to Node 24-based `checkout@v6` and `setup-python@v6`
- pinned the CI Ruff version for reproducible linting

### Security

- duplicate JSON keys are rejected
- malformed, oversized, or cross-session request IDs are rejected
- unsupported or incomplete agent capabilities fail the handshake
- response IDs, command names, output types, and boolean result state are validated
- the loopback-only and no-shell design remains unchanged

## 2.0.0

- replaced the original unrestricted reverse-shell proof of concept with a loopback-only protocol simulator
- introduced explicit allowlisted commands
- added length-prefixed JSON framing
- added automated unit/integration tests and GitHub Actions CI
