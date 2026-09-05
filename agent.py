"""Loopback-only agent for the Python C2 protocol lab simulator."""

from __future__ import annotations

import argparse
import socket
import sys

from commands import VERSION, agent_metadata, execute_command
from protocol import (
    PROTOCOL_VERSION,
    ProtocolError,
    recv_message,
    send_message,
    validate_request_id,
)

LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 5555
CONNECT_TIMEOUT = 5.0
HANDSHAKE_TIMEOUT = 5.0


def handle_session(sock: socket.socket) -> None:
    """Run one simulator session over an already-connected socket."""
    send_message(
        sock,
        {
            "type": "hello",
            "protocol": PROTOCOL_VERSION,
            "agent": agent_metadata(),
        },
    )

    sock.settimeout(HANDSHAKE_TIMEOUT)
    reply = recv_message(sock)
    if reply.get("type") != "hello_ack":
        raise ProtocolError("expected hello_ack")
    if reply.get("protocol") != PROTOCOL_VERSION:
        raise ProtocolError("protocol version mismatch")
    session_id = validate_request_id(reply.get("session_id"))
    sock.settimeout(None)

    while True:
        message = recv_message(sock)
        if message.get("type") != "command":
            send_message(
                sock,
                {
                    "type": "error",
                    "error": "expected command message",
                },
            )
            continue

        try:
            request_id = validate_request_id(message.get("request_id"))
        except ProtocolError as exc:
            send_message(
                sock,
                {
                    "type": "error",
                    "error": str(exc),
                },
            )
            continue

        if not request_id.startswith(f"{session_id}-"):
            send_message(
                sock,
                {
                    "type": "error",
                    "request_id": request_id,
                    "error": "request_id does not belong to the active session",
                },
            )
            continue

        command_line = message.get("command")
        if not isinstance(command_line, str):
            send_message(
                sock,
                {
                    "type": "error",
                    "request_id": request_id,
                    "error": "command must be a string",
                },
            )
            continue

        result = execute_command(command_line)
        result["request_id"] = request_id
        send_message(sock, result)

        if result.get("ok") is True and result.get("command") == "exit":
            return


def run_agent(port: int) -> int:
    """Connect to the loopback controller and process one lab session."""
    try:
        with socket.create_connection(
            (LOOPBACK_HOST, port),
            timeout=CONNECT_TIMEOUT,
        ) as sock:
            handle_session(sock)
        return 0
    except KeyboardInterrupt:
        print("\n[!] agent interrupted", file=sys.stderr)
        return 130
    except (ConnectionError, OSError, EOFError, ProtocolError) as exc:
        print(f"[!] agent error: {exc}", file=sys.stderr)
        return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Loopback-only C2 protocol lab agent (no arbitrary shell execution)."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"controller port on {LOOPBACK_HOST} (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Python C2 Lab Simulator v{VERSION}",
    )
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    return args


def main() -> int:
    args = parse_args()
    return run_agent(args.port)


if __name__ == "__main__":
    raise SystemExit(main())
