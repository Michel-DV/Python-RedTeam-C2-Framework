"""Length-prefixed JSON framing used by the local C2 lab simulator."""

from __future__ import annotations

import json
import struct
from socket import socket
from typing import Any

PROTOCOL_VERSION = 2
MAX_FRAME_SIZE = 64 * 1024
MAX_REQUEST_ID_LENGTH = 64
_HEADER = struct.Struct("!I")


class ProtocolError(RuntimeError):
    """Raised when a peer sends an invalid protocol frame."""


def send_message(sock: socket, message: dict[str, Any]) -> None:
    """Serialize and send one JSON message using a 4-byte network-order length prefix."""
    if not isinstance(message, dict):
        raise ProtocolError("message must be a JSON object")

    try:
        payload = json.dumps(
            message,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ProtocolError("message is not JSON serializable") from exc

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
        message = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("invalid JSON frame") from exc

    if not isinstance(message, dict):
        raise ProtocolError("top-level JSON value must be an object")
    return message


def validate_request_id(value: Any) -> str:
    """Validate a request identifier used to correlate command/result messages."""
    if not isinstance(value, str):
        raise ProtocolError("request_id must be a string")
    if not value:
        raise ProtocolError("request_id must not be empty")
    if len(value) > MAX_REQUEST_ID_LENGTH:
        raise ProtocolError(f"request_id exceeds {MAX_REQUEST_ID_LENGTH} characters")
    if not all(33 <= ord(ch) <= 126 for ch in value):
        raise ProtocolError("request_id must contain printable ASCII without whitespace")
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _recv_exact(sock: socket, size: int) -> bytes:
    chunks = bytearray(size)
    view = memoryview(chunks)
    received = 0

    while received < size:
        count = sock.recv_into(view[received:], size - received)
        if count == 0:
            raise EOFError("peer closed the connection")
        received += count

    return bytes(chunks)
