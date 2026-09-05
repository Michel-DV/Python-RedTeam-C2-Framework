from __future__ import annotations

import socket
import threading
import unittest

from agent import handle_session
from protocol import PROTOCOL_VERSION, recv_message, send_message


class AgentSessionTests(unittest.TestCase):
    def test_handshake_ping_and_exit(self) -> None:
        controller, agent_sock = socket.socketpair()
        errors: list[BaseException] = []

        def run_agent() -> None:
            try:
                with agent_sock:
                    handle_session(agent_sock)
            except BaseException as exc:  # pragma: no cover - surfaced below
                errors.append(exc)

        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()

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
        errors: list[BaseException] = []

        def run_agent() -> None:
            try:
                with agent_sock:
                    handle_session(agent_sock)
            except BaseException as exc:  # pragma: no cover - surfaced below
                errors.append(exc)

        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()

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


if __name__ == "__main__":
    unittest.main()
