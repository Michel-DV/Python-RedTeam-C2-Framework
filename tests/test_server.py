from __future__ import annotations

import socket
import threading
import unittest

from commands import capabilities
from protocol import PROTOCOL_VERSION, ProtocolError, recv_message, send_message
from server import perform_handshake


def _agent_metadata() -> dict[str, object]:
    return {
        "hostname": "lab-host",
        "user": "analyst",
        "platform": "TestOS",
        "python": "3.11.0",
        "simulator_version": "2.1.0",
        "capabilities": capabilities(),
    }


def _run_handshake_with_metadata(metadata: dict[str, object]) -> list[BaseException]:
    server_sock, agent_sock = socket.socketpair()
    errors: list[BaseException] = []

    def run_handshake() -> None:
        try:
            with server_sock:
                perform_handshake(server_sock)
        except BaseException as exc:  # pragma: no cover - asserted by callers
            errors.append(exc)

    thread = threading.Thread(target=run_handshake, daemon=True)
    thread.start()

    with agent_sock:
        send_message(
            agent_sock,
            {
                "type": "hello",
                "protocol": PROTOCOL_VERSION,
                "agent": metadata,
            },
        )

    thread.join(timeout=2)
    if thread.is_alive():
        raise AssertionError("handshake thread did not exit")
    return errors


class ServerHandshakeTests(unittest.TestCase):
    def test_valid_handshake(self) -> None:
        server_sock, agent_sock = socket.socketpair()
        results: list[tuple[dict[str, object], str, set[str]]] = []
        errors: list[BaseException] = []

        def run_handshake() -> None:
            try:
                with server_sock:
                    results.append(perform_handshake(server_sock))
            except BaseException as exc:  # pragma: no cover - surfaced below
                errors.append(exc)

        thread = threading.Thread(target=run_handshake, daemon=True)
        thread.start()

        with agent_sock:
            send_message(
                agent_sock,
                {
                    "type": "hello",
                    "protocol": PROTOCOL_VERSION,
                    "agent": _agent_metadata(),
                },
            )
            ack = recv_message(agent_sock)
            self.assertEqual(ack["type"], "hello_ack")
            self.assertEqual(ack["protocol"], PROTOCOL_VERSION)
            self.assertIsInstance(ack["session_id"], str)
            self.assertTrue(ack["session_id"])

        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

        self.assertEqual(len(results), 1)
        agent, session_id, allowed = results[0]
        self.assertEqual(agent["hostname"], "lab-host")
        self.assertEqual(session_id, ack["session_id"])
        self.assertEqual(allowed, set(capabilities()))

    def test_unexpected_capability_is_rejected(self) -> None:
        metadata = _agent_metadata()
        metadata["capabilities"] = [*capabilities(), "shell"]
        errors = _run_handshake_with_metadata(metadata)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], ProtocolError)
        self.assertIn("unsupported capabilities", str(errors[0]))

    def test_missing_required_capability_is_rejected(self) -> None:
        metadata = _agent_metadata()
        metadata["capabilities"] = [item for item in capabilities() if item != "exit"]
        errors = _run_handshake_with_metadata(metadata)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], ProtocolError)
        self.assertIn("missing required capabilities", str(errors[0]))

    def test_control_characters_in_metadata_are_rejected(self) -> None:
        metadata = _agent_metadata()
        metadata["hostname"] = "lab-host\nspoofed"
        errors = _run_handshake_with_metadata(metadata)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], ProtocolError)
        self.assertIn("control characters", str(errors[0]))


if __name__ == "__main__":
    unittest.main()
