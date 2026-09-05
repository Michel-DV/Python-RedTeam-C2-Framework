from __future__ import annotations

import socket
import struct
import unittest

from protocol import MAX_FRAME_SIZE, ProtocolError, recv_message, send_message


class ProtocolTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        left, right = socket.socketpair()
        with left, right:
            message = {"type": "command", "command": "ping"}
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


if __name__ == "__main__":
    unittest.main()
