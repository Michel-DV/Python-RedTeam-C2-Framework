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
- branch coverage measurement with a 90% quality gate
- downloadable HTML coverage report artifact
- expanded controller/agent runtime and protocol tests
- terminal demo SVG and asciinema-compatible recording
- prepared v2.1.0 release notes
- protocol documentation
- security policy

### Changed

- reduced the maximum protocol frame from 1 MiB to 64 KiB
- tightened command and echo input limits
- improved graceful interruption handling
- expanded tests for malformed frames, invalid request IDs, duplicate JSON keys, metadata validation, command validation, and CLI/runtime paths
- updated GitHub Actions to Node 24-based `checkout@v6` and `setup-python@v6`
- added `upload-artifact@v7` for coverage reports
- pinned CI Ruff and coverage.py versions for reproducible quality checks
- removed an unreachable empty-payload branch from protocol serialization

### Quality snapshot

- 44 tests passing during release preparation
- 91.8% overall branch coverage
- `protocol.py` at 100% branch coverage
- CI matrix passing on Python 3.11, 3.12, and 3.13

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
