# Protocol v2

The simulator uses a small request/response protocol over a loopback-only TCP connection.

## Transport

Every message is encoded as:

```text
4-byte unsigned big-endian length
UTF-8 JSON object
```

The maximum JSON payload is 64 KiB.

The decoder rejects:

- zero-length frames
- frames larger than the configured limit
- truncated frames
- invalid UTF-8
- invalid JSON
- duplicate object keys
- non-object top-level JSON values

## Session flow

```text
agent                         controller
  |                               |
  | hello                         |
  |------------------------------>|
  |                               |
  | hello_ack + session_id        |
  |<------------------------------|
  |                               |
  | command + request_id          |
  |<------------------------------|
  |                               |
  | result + same request_id      |
  |------------------------------>|
  |                               |
```

## `hello`

Sent by the agent immediately after connecting.

```json
{
  "type": "hello",
  "protocol": 2,
  "agent": {
    "hostname": "lab-host",
    "user": "analyst",
    "platform": "Linux",
    "python": "3.13.0",
    "simulator_version": "2.1.0",
    "capabilities": ["help", "ping", "hostname", "whoami", "cwd", "platform", "python", "time", "echo", "exit"]
  }
}
```

The controller validates required metadata, rejects capabilities outside its own local allowlist, and requires the basic `help` and `exit` capabilities so the interactive session remains controllable.

## `hello_ack`

Sent by the controller after a successful handshake.

```json
{
  "type": "hello_ack",
  "protocol": 2,
  "session_id": "0123456789abcdef",
  "message": "lab session accepted"
}
```

The session identifier is used as part of request correlation. It is not an authentication token and must not be treated as one.

## `command`

```json
{
  "type": "command",
  "request_id": "0123456789abcdef-1",
  "command": "ping"
}
```

Request identifiers must be non-empty printable ASCII without whitespace and are limited to 64 characters. The agent also requires every request ID to begin with the active session ID followed by `-`.

The controller sends only commands present in the validated allowlist.

## `result`

```json
{
  "type": "result",
  "request_id": "0123456789abcdef-1",
  "ok": true,
  "command": "ping",
  "output": "pong"
}
```

The controller requires the response `request_id` to exactly match the currently active request. It also validates that `ok` is a boolean, `output` is a string, and the returned command name matches the request.

## `error`

Protocol-level errors use:

```json
{
  "type": "error",
  "request_id": "0123456789abcdef-1",
  "error": "description"
}
```

When an incoming request ID itself is invalid, the error response omits `request_id` rather than reflecting malformed peer input.

## Command limits

The simulator intentionally bounds input:

- command line: 512 characters
- `echo` text: 256 characters
- metadata string: 256 characters
- protocol frame: 64 KiB
- request ID: 64 characters

## Security boundary

Protocol v2 is designed only for local education and testing on `127.0.0.1`. It does not implement authentication, encryption, remote deployment, arbitrary process execution, persistence, file transfer, or shell access.
