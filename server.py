"""Loopback-only controller for the Python C2 protocol lab simulator."""

from __future__ import annotations

import argparse
import socket
import sys
from typing import Any

from protocol import PROTOCOL_VERSION, ProtocolError, recv_message, send_message

LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 5555


def perform_handshake(client: socket.socket) -> dict[str, Any]:
    hello = recv_message(client)
    if hello.get("type") != "hello":
        raise ProtocolError("expected hello message")
    if hello.get("protocol") != PROTOCOL_VERSION:
        raise ProtocolError("protocol version mismatch")

    agent = hello.get("agent")
    if not isinstance(agent, dict):
        raise ProtocolError("hello message missing agent metadata")

    send_message(
        client,
        {
            "type": "hello_ack",
            "protocol": PROTOCOL_VERSION,
            "message": "lab session accepted",
        },
    )
    return agent


def run_session(client: socket.socket) -> None:
    agent = perform_handshake(client)
    print("[+] Lab agent connected")
    print(f"    host: {agent.get('hostname', 'unknown')}")
    print(f"    user: {agent.get('user', 'unknown')}")
    print(f"    platform: {agent.get('platform', 'unknown')}")
    print("    type 'help' for supported simulator commands")

    while True:
        try:
            command = input("lab-c2> ").strip()
        except (EOFError, KeyboardInterrupt):
            command = "exit"
            print()

        if not command:
            continue

        send_message(
            client,
            {
                "type": "command",
                "command": command,
            },
        )

        response = recv_message(client)
        response_type = response.get("type")

        if response_type == "error":
            print(f"[!] protocol error from agent: {response.get('error', 'unknown error')}")
            continue
        if response_type != "result":
            raise ProtocolError(f"unexpected response type: {response_type!r}")

        output = response.get("output", "")
        if output:
            print(output)

        if command.split(maxsplit=1)[0].lower() == "exit" and response.get("ok") is True:
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
                print(f"[*] Connection from {address[0]}:{address[1]}")
                run_session(client)
        return 0
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
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    return args


def main() -> int:
    args = parse_args()
    return run_server(args.port)


if __name__ == "__main__":
    raise SystemExit(main())
