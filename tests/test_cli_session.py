from __future__ import annotations

import contextlib
import io
import socket
import threading
import unittest
from unittest.mock import MagicMock, patch

import agent
import server
from agent import handle_session


class EndToEndSessionTests(unittest.TestCase):
    def _run_agent_thread(self, agent_sock: socket.socket) -> tuple[threading.Thread, list[BaseException]]:
        errors: list[BaseException] = []

        def target() -> None:
            try:
                with agent_sock:
                    handle_session(agent_sock)
            except BaseException as exc:  # pragma: no cover - surfaced by the test
                errors.append(exc)

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        return thread, errors

    def test_controller_and_agent_complete_safe_session(self) -> None:
        controller, agent_sock = socket.socketpair()
        thread, errors = self._run_agent_thread(agent_sock)
        stdout = io.StringIO()

        with controller, patch(
            "builtins.input",
            side_effect=["ping", "echo protocol test", "exit"],
        ), contextlib.redirect_stdout(stdout):
            server.run_session(controller)

        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

        output = stdout.getvalue()
        self.assertIn("Lab agent connected", output)
        self.assertIn("pong", output)
        self.assertIn("protocol test", output)
        self.assertIn("session closing", output)

    def test_controller_rejects_bad_local_input_before_transmission(self) -> None:
        controller, agent_sock = socket.socketpair()
        thread, errors = self._run_agent_thread(agent_sock)
        stdout = io.StringIO()

        with controller, patch(
            "builtins.input",
            side_effect=["", 'echo "unterminated', "not-a-command", "exit"],
        ), contextlib.redirect_stdout(stdout):
            server.run_session(controller)

        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

        output = stdout.getvalue()
        self.assertIn("parse error", output)
        self.assertIn("unsupported simulator command", output)

    def test_eof_requests_clean_exit(self) -> None:
        controller, agent_sock = socket.socketpair()
        thread, errors = self._run_agent_thread(agent_sock)
        stdout = io.StringIO()

        with controller, patch("builtins.input", side_effect=EOFError), contextlib.redirect_stdout(stdout):
            server.run_session(controller)

        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]
        self.assertIn("session closing", stdout.getvalue())


class AgentRuntimeTests(unittest.TestCase):
    def test_run_agent_success(self) -> None:
        sock = MagicMock()
        context = MagicMock()
        context.__enter__.return_value = sock
        context.__exit__.return_value = False

        with patch("agent.socket.create_connection", return_value=context), patch(
            "agent.handle_session"
        ) as handle:
            self.assertEqual(agent.run_agent(5555), 0)

        handle.assert_called_once_with(sock)

    def test_run_agent_connection_error(self) -> None:
        stderr = io.StringIO()
        with patch("agent.socket.create_connection", side_effect=OSError("offline")), contextlib.redirect_stderr(stderr):
            self.assertEqual(agent.run_agent(5555), 1)
        self.assertIn("agent error", stderr.getvalue())

    def test_run_agent_keyboard_interrupt(self) -> None:
        stderr = io.StringIO()
        with patch("agent.socket.create_connection", side_effect=KeyboardInterrupt), contextlib.redirect_stderr(stderr):
            self.assertEqual(agent.run_agent(5555), 130)
        self.assertIn("agent interrupted", stderr.getvalue())

    def test_agent_parse_args(self) -> None:
        self.assertEqual(agent.parse_args(["--port", "6000"]).port, 6000)
        with self.assertRaises(SystemExit):
            agent.parse_args(["--port", "0"])


class ServerRuntimeTests(unittest.TestCase):
    @staticmethod
    def _socket_context(address: tuple[str, int] = ("127.0.0.1", 49152)) -> tuple[MagicMock, MagicMock]:
        server_sock = MagicMock()
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        server_sock.accept.return_value = (client, address)

        context = MagicMock()
        context.__enter__.return_value = server_sock
        context.__exit__.return_value = False
        return context, server_sock

    def test_run_server_success(self) -> None:
        context, server_sock = self._socket_context()
        stdout = io.StringIO()
        with patch("server.socket.socket", return_value=context), patch(
            "server.run_session"
        ) as run_session, contextlib.redirect_stdout(stdout):
            self.assertEqual(server.run_server(5555), 0)

        server_sock.bind.assert_called_once_with((server.LOOPBACK_HOST, 5555))
        server_sock.listen.assert_called_once_with(1)
        run_session.assert_called_once()
        self.assertIn("Connection from 127.0.0.1", stdout.getvalue())

    def test_run_server_rejects_non_loopback_peer(self) -> None:
        context, _ = self._socket_context(("192.0.2.10", 49152))
        stderr = io.StringIO()
        with patch("server.socket.socket", return_value=context), contextlib.redirect_stderr(stderr):
            self.assertEqual(server.run_server(5555), 1)
        self.assertIn("non-loopback peer rejected", stderr.getvalue())

    def test_run_server_keyboard_interrupt(self) -> None:
        context, server_sock = self._socket_context()
        server_sock.accept.side_effect = KeyboardInterrupt
        stderr = io.StringIO()
        with patch("server.socket.socket", return_value=context), contextlib.redirect_stderr(stderr):
            self.assertEqual(server.run_server(5555), 130)
        self.assertIn("server interrupted", stderr.getvalue())

    def test_server_parse_args_and_metadata_display(self) -> None:
        self.assertEqual(server.parse_args(["--port", "6000"]).port, 6000)
        with self.assertRaises(SystemExit):
            server.parse_args(["--port", "70000"])

        self.assertEqual(server._display_metadata({"hostname": "lab\thost"}, "hostname"), "lab host")
        self.assertEqual(server._display_metadata({"hostname": 42}, "hostname"), "unknown")


if __name__ == "__main__":
    unittest.main()
