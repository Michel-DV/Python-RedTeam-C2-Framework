from __future__ import annotations

import socket
import struct
import unittest

from protocol import (
    MAX_FRAME_SIZE,
    ProtocolError,
    recv_message,
    send_message,
    validate_request_id,
)


class ProtocolTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        left, right = socket.socketpair()
        with left, right:
            message = {"type": "command", "request_id": "abc-1", "command": "ping"}
            send_message(left, message)
            self.assertEqual(recv_message(right), message)

    def test_rejects_zero_length_frame(self) -> None:
        left, right = socket.socketpair()
        with left, right:
            left.sendall(struct.pack("!I", 0))
            with self.assertRaises(ProtocolError):
                recv_message(right)

    def test_rejects_oversized_frame_header(self) -> None:
        left, right = socket.socketpair()
        with left, right:
            left.sendall(struct.pack("!I", MAX_FRAME_SIZE + 1))
            with self.assertRaises(ProtocolError):
                recv_message(right)

    def test_send_rejects_oversized_payload(self) -> None:
        left, right = socket.socketpair()
        with left, right:
            with self.assertRaises(ProtocolError):
                send_message(left, {"data": "x" * (MAX_FRAME_SIZE + 1)})

    def test_rejects_non_object_json(self) -> None:
        left, right = socket.socketpair()
        with left, right:
            payload = b"[]"
            left.sendall(struct.pack("!I", len(payload)) + payload)
            with self.assertRaises(ProtocolError):
                recv_message(right)

    def test_rejects_duplicate_json_keys(self) -> None:
        left, right = socket.socketpair()
        with left, right:
            payload = b'{"type":"hello","type":"command"}'
            left.sendall(struct.pack("!I", len(payload)) + payload)
            with self.assertRaises(ProtocolError):
                recv_message(right)

    def test_request_id_validation(self) -> None:
        self.assertEqual(validate_request_id("session-1"), "session-1")
        for invalid in (None, "", "with space", "bad\nline"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ProtocolError):
                    validate_request_id(invalid)


if __name__ == "__main__":
    unittest.main()
