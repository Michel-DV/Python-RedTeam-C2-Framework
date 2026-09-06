from __future__ import annotations

import unittest
from unittest.mock import patch

import commands
from commands import (
    MAX_COMMAND_LENGTH,
    MAX_ECHO_LENGTH,
    agent_metadata,
    capabilities,
    execute_command,
)


class CommandTests(unittest.TestCase):
    def test_ping(self) -> None:
        result = execute_command("ping")
        self.assertTrue(result["ok"])
        self.assertEqual(result["output"], "pong")

    def test_echo(self) -> None:
        result = execute_command('echo "hello lab"')
        self.assertTrue(result["ok"])
        self.assertEqual(result["output"], "hello lab")

    def test_help_and_exit(self) -> None:
        help_result = execute_command("help")
        self.assertTrue(help_result["ok"])
        self.assertIn("Available commands", str(help_result["output"]))

        self.assertFalse(execute_command("help extra")["ok"])
        self.assertFalse(execute_command("exit now")["ok"])
        self.assertTrue(execute_command("exit")["ok"])

    def test_blank_and_non_string_commands_are_rejected(self) -> None:
        self.assertFalse(execute_command(42)["ok"])  # type: ignore[arg-type]
        self.assertFalse(execute_command("   ")["ok"])

    def test_unknown_command_is_rejected(self) -> None:
        result = execute_command("uname -a")
        self.assertFalse(result["ok"])
        self.assertIn("unsupported command", str(result["output"]))

    def test_extra_args_are_rejected(self) -> None:
        result = execute_command("hostname extra")
        self.assertFalse(result["ok"])

    def test_simple_commands_return_strings(self) -> None:
        for name in ("hostname", "whoami", "cwd", "platform", "python", "time"):
            with self.subTest(name=name):
                result = execute_command(name)
                self.assertTrue(result["ok"])
                self.assertIsInstance(result["output"], str)

    def test_handler_os_error_is_reported(self) -> None:
        def fail() -> str:
            raise OSError("boom")

        with patch.dict(commands._SIMPLE_COMMANDS, {"hostname": fail}):
            result = execute_command("hostname")
        self.assertFalse(result["ok"])
        self.assertIn("command failed", str(result["output"]))

    def test_capabilities_are_explicit(self) -> None:
        allowed = capabilities()
        self.assertIn("ping", allowed)
        self.assertIn("exit", allowed)
        self.assertNotIn("shell", allowed)
        self.assertEqual(len(allowed), len(set(allowed)))

    def test_agent_metadata_shape(self) -> None:
        metadata = agent_metadata()
        for field in (
            "hostname",
            "user",
            "platform",
            "python",
            "pid",
            "simulator_version",
            "capabilities",
            "executable",
        ):
            self.assertIn(field, metadata)
        self.assertEqual(metadata["simulator_version"], commands.VERSION)
        self.assertEqual(metadata["capabilities"], capabilities())

    def test_command_length_is_limited(self) -> None:
        result = execute_command("x" * (MAX_COMMAND_LENGTH + 1))
        self.assertFalse(result["ok"])
        self.assertIn("exceeds", str(result["output"]))

    def test_echo_length_is_limited(self) -> None:
        result = execute_command("echo " + ("a" * (MAX_ECHO_LENGTH + 1)))
        self.assertFalse(result["ok"])
        self.assertIn("echo text exceeds", str(result["output"]))

    def test_nul_byte_is_rejected(self) -> None:
        result = execute_command("echo hello\x00world")
        self.assertFalse(result["ok"])
        self.assertIn("NUL", str(result["output"]))

    def test_unbalanced_quotes_are_rejected(self) -> None:
        result = execute_command('echo "unterminated')
        self.assertFalse(result["ok"])
        self.assertIn("parse error", str(result["output"]))


if __name__ == "__main__":
    unittest.main()
