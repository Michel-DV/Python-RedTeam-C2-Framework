"""Loopback-only controller for the Python C2 protocol lab simulator."""

from __future__ import annotations

import argparse
import secrets
import shlex
import socket
import sys
from typing import Any

from commands import VERSION, capabilities
from protocol import (
    PROTOCOL_VERSION,
    ProtocolError,
    recv_message,
    send_message,
    validate_request_id,
)

LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 5555
HANDSHAKE_TIMEOUT = 5.0
_MAX_METADATA_LENGTH = 256


def perform_handshake(client: socket.socket) -> tuple[dict[str, Any], str, set[str]]:
    """Validate the lab agent hello message and acknowledge the session."""
    hello = recv_message(client)
    if hello.get("type") != "hello":
        raise ProtocolError("expected hello message")
    if hello.get("protocol") != PROTOCOL_VERSION:
        raise ProtocolError("protocol version mismatch")

    agent = hello.get("agent")
    if not isinstance(agent, dict):
        raise ProtocolError("hello message missing agent metadata")

    _validate_agent_metadata(agent)
    allowed_commands = _validate_capabilities(agent.get("capabilities"))
    session_id = secrets.token_hex(8)

    send_message(
        client,
        {
            "type": "hello_ack",
            "protocol": PROTOCOL_VERSION,
            "session_id": session_id,
            "message": "lab session accepted",
        },
    )
    return agent, session_id, allowed_commands


def run_session(client: socket.socket) -> None:
    client.settimeout(HANDSHAKE_TIMEOUT)
    agent, session_id, allowed_commands = perform_handshake(client)
    client.settimeout(None)

    print("[+] Lab agent connected")
    print(f"    host: {_display_metadata(agent, 'hostname')}")
    print(f"    user: {_display_metadata(agent, 'user')}")
    print(f"    platform: {_display_metadata(agent, 'platform')}")
    print(f"    simulator: {_display_metadata(agent, 'simulator_version')}")
    print("    type 'help' for supported simulator commands")

    request_counter = 0
    while True:
        try:
            command = input("lab-c2> ").strip()
        except (EOFError, KeyboardInterrupt):
            command = "exit"
            print()

        if not command:
            continue

        try:
            parts = shlex.split(command)
        except ValueError as exc:
            print(f"[!] parse error: {exc}")
            continue

        if not parts:
            continue

        command_name = parts[0].lower()
        if command_name not in allowed_commands:
            print(
                f"[!] unsupported simulator command: {command_name}. "
                "Type 'help' for the allowlist."
            )
            continue

        request_counter += 1
        request_id = f"{session_id}-{request_counter}"
        validate_request_id(request_id)

        send_message(
            client,
            {
                "type": "command",
                "request_id": request_id,
                "command": command,
            },
        )

        response = recv_message(client)
        response_id = validate_request_id(response.get("request_id"))
        if response_id != request_id:
            raise ProtocolError("response request_id does not match the active request")

        response_type = response.get("type")
        if response_type == "error":
            print(f"[!] protocol error from agent: {response.get('error', 'unknown error')}")
            continue
        if response_type != "result":
            raise ProtocolError(f"unexpected response type: {response_type!r}")

        output = response.get("output", "")
        if not isinstance(output, str):
            raise ProtocolError("result output must be a string")
        if output:
            print(output)

        if command_name == "exit" and response.get("ok") is True:
            return


def run_server(port: int) -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((LOOPBACK_HOST, port))
            server.listen(1)
            print(f"[*] Listening on {LOOPBACK_HOST}:{port}")
            print("[*] Loopback-only lab mode; remote clients are intentionally unsupported")

            client, address = server.accept()
            with client:
                if address[0] != LOOPBACK_HOST:
                    raise ProtocolError("non-loopback peer rejected")
                print(f"[*] Connection from {address[0]}:{address[1]}")
                run_session(client)
        return 0
    except KeyboardInterrupt:
        print("\n[!] server interrupted", file=sys.stderr)
        return 130
    except (OSError, EOFError, ProtocolError) as exc:
        print(f"[!] server error: {exc}", file=sys.stderr)
        return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Loopback-only C2 protocol lab controller."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"loopback listen port (default: {DEFAULT_PORT})",
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


def _validate_capabilities(value: Any) -> set[str]:
    if not isinstance(value, list) or not value:
        raise ProtocolError("agent capabilities must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise ProtocolError("agent capabilities must contain non-empty strings")
    if len(value) != len(set(value)):
        raise ProtocolError("agent capabilities contain duplicates")

    supported = set(capabilities())
    reported = set(value)
    unexpected = reported - supported
    if unexpected:
        raise ProtocolError(
            "agent reported unsupported capabilities: " + ", ".join(sorted(unexpected))
        )
    return reported


def _validate_agent_metadata(agent: dict[str, Any]) -> None:
    for field in ("hostname", "user", "platform", "python", "simulator_version"):
        value = agent.get(field)
        if not isinstance(value, str) or not value:
            raise ProtocolError(f"agent metadata field {field!r} must be a non-empty string")
        if len(value) > _MAX_METADATA_LENGTH:
            raise ProtocolError(f"agent metadata field {field!r} is too long")
        if any(ord(ch) < 32 and ch not in "\t" for ch in value):
            raise ProtocolError(f"agent metadata field {field!r} contains control characters")


def _display_metadata(agent: dict[str, Any], field: str) -> str:
    value = agent.get(field, "unknown")
    if not isinstance(value, str):
        return "unknown"
    return value.replace("\t", " ")


def main() -> int:
    args = parse_args()
    return run_server(args.port)


if __name__ == "__main__":
    raise SystemExit(main())
