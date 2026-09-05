"""Length-prefixed JSON framing used by the local C2 lab simulator."""

from __future__ import annotations

import json
import struct
from socket import socket
from typing import Any

PROTOCOL_VERSION = 1
MAX_FRAME_SIZE = 1024 * 1024
_HEADER = struct.Struct("!I")


class ProtocolError(RuntimeError):
    """Raised when a peer sends an invalid protocol frame."""


def send_message(sock: socket, message: dict[str, Any]) -> None:
    """Serialize and send one JSON message using a 4-byte network-order length prefix."""
    payload = json.dumps(
        message,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    if not payload:
        raise ProtocolError("empty payload")
    if len(payload) > MAX_FRAME_SIZE:
        raise ProtocolError(f"frame exceeds {MAX_FRAME_SIZE} bytes")

    sock.sendall(_HEADER.pack(len(payload)) + payload)


def recv_message(sock: socket) -> dict[str, Any]:
    """Receive and decode one length-prefixed JSON message."""
    header = _recv_exact(sock, _HEADER.size)
    (length,) = _HEADER.unpack(header)

    if length == 0:
        raise ProtocolError("zero-length frame")
    if length > MAX_FRAME_SIZE:
        raise ProtocolError(f"frame exceeds {MAX_FRAME_SIZE} bytes")

    raw = _recv_exact(sock, length)
    try:
        message = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("invalid JSON frame") from exc

    if not isinstance(message, dict):
        raise ProtocolError("top-level JSON value must be an object")
    return message


def _recv_exact(sock: socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise EOFError("peer closed the connection")
        chunks.extend(chunk)
    return bytes(chunks)
