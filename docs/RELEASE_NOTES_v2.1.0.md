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
- **90% minimum branch-coverage quality gate**
- **91.8% measured branch coverage** at release preparation time
- Downloadable HTML coverage report artifact from CI
- New protocol and security documentation
- Terminal demo preview plus asciinema-compatible recording

## Validation snapshot

The release-prep CI executed **44 tests** successfully. Coverage on Python 3.13 measured:

| Module | Branch coverage |
| --- | ---: |
| `agent.py` | 97.6% |
| `commands.py` | 97.7% |
| `protocol.py` | 100.0% |
| `server.py` | 83.6% |
| **Overall** | **91.8%** |

CI also validates Ruff lint, Ruff formatting, compile checks, and the complete test suite on Python 3.11, 3.12, and 3.13.

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

## Suggested GitHub release metadata

**Tag:** `v2.1.0`  
**Title:** `Python C2 Lab Simulator v2.1.0`  
**Target:** `main`

Use this document as the GitHub Release body.
