from __future__ import annotations

import socket
import threading
import unittest

from agent import handle_session
from protocol import PROTOCOL_VERSION, ProtocolError, recv_message, send_message


class AgentSessionTests(unittest.TestCase):
    @staticmethod
    def _start_agent(agent_sock: socket.socket) -> tuple[threading.Thread, list[BaseException]]:
        errors: list[BaseException] = []

        def run_agent() -> None:
            try:
                with agent_sock:
                    handle_session(agent_sock)
            except BaseException as exc:  # pragma: no cover - surfaced below
                errors.append(exc)

        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()
        return thread, errors

    def test_handshake_ping_and_exit(self) -> None:
        controller, agent_sock = socket.socketpair()
        thread, errors = self._start_agent(agent_sock)

        with controller:
            hello = recv_message(controller)
            self.assertEqual(hello["type"], "hello")
            self.assertEqual(hello["protocol"], PROTOCOL_VERSION)
            self.assertIn("capabilities", hello["agent"])

            send_message(
                controller,
                {
                    "type": "hello_ack",
                    "protocol": PROTOCOL_VERSION,
                    "session_id": "test-session",
                },
            )

            send_message(
                controller,
                {
                    "type": "command",
                    "request_id": "test-session-1",
                    "command": "ping",
                },
            )
            ping = recv_message(controller)
            self.assertTrue(ping["ok"])
            self.assertEqual(ping["output"], "pong")
            self.assertEqual(ping["request_id"], "test-session-1")

            send_message(
                controller,
                {
                    "type": "command",
                    "request_id": "test-session-2",
                    "command": "exit",
                },
            )
            bye = recv_message(controller)
            self.assertTrue(bye["ok"])
            self.assertEqual(bye["command"], "exit")
            self.assertEqual(bye["request_id"], "test-session-2")

        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

    def test_invalid_request_ids_are_rejected(self) -> None:
        controller, agent_sock = socket.socketpair()
        thread, errors = self._start_agent(agent_sock)

        with controller:
            hello = recv_message(controller)
            self.assertEqual(hello["type"], "hello")
            send_message(
                controller,
                {
                    "type": "hello_ack",
                    "protocol": PROTOCOL_VERSION,
                    "session_id": "test-session",
                },
            )

            send_message(controller, {"type": "command", "command": "ping"})
            response = recv_message(controller)
            self.assertEqual(response["type"], "error")
            self.assertIn("request_id", str(response["error"]))

            send_message(
                controller,
                {
                    "type": "command",
                    "request_id": "other-session-1",
                    "command": "ping",
                },
            )
            response = recv_message(controller)
            self.assertEqual(response["type"], "error")
            self.assertEqual(response["request_id"], "other-session-1")
            self.assertIn("active session", str(response["error"]))

            send_message(
                controller,
                {
                    "type": "command",
                    "request_id": "test-session-3",
                    "command": "exit",
                },
            )
            recv_message(controller)

        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

    def test_unexpected_message_and_non_string_command_are_rejected(self) -> None:
        controller, agent_sock = socket.socketpair()
        thread, errors = self._start_agent(agent_sock)

        with controller:
            recv_message(controller)
            send_message(
                controller,
                {
                    "type": "hello_ack",
                    "protocol": PROTOCOL_VERSION,
                    "session_id": "test-session",
                },
            )

            send_message(controller, {"type": "status"})
            response = recv_message(controller)
            self.assertEqual(response["type"], "error")
            self.assertIn("expected command", str(response["error"]))

            send_message(
                controller,
                {
                    "type": "command",
                    "request_id": "test-session-1",
                    "command": 123,
                },
            )
            response = recv_message(controller)
            self.assertEqual(response["type"], "error")
            self.assertEqual(response["request_id"], "test-session-1")
            self.assertIn("string", str(response["error"]))

            send_message(
                controller,
                {
                    "type": "command",
                    "request_id": "test-session-2",
                    "command": "exit",
                },
            )
            recv_message(controller)

        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

    def test_bad_handshake_is_rejected(self) -> None:
        for ack in (
            {"type": "wrong", "protocol": PROTOCOL_VERSION, "session_id": "test-session"},
            {"type": "hello_ack", "protocol": 999, "session_id": "test-session"},
        ):
            with self.subTest(ack=ack):
                controller, agent_sock = socket.socketpair()
                thread, errors = self._start_agent(agent_sock)
                with controller:
                    recv_message(controller)
                    send_message(controller, ack)

                thread.join(timeout=2)
                self.assertFalse(thread.is_alive())
                self.assertEqual(len(errors), 1)
                self.assertIsInstance(errors[0], ProtocolError)


if __name__ == "__main__":
    unittest.main()
