from __future__ import annotations

import unittest

from commands import MAX_COMMAND_LENGTH, MAX_ECHO_LENGTH, capabilities, execute_command


class CommandTests(unittest.TestCase):
    def test_ping(self) -> None:
        result = execute_command("ping")
        self.assertTrue(result["ok"])
        self.assertEqual(result["output"], "pong")

    def test_echo(self) -> None:
        result = execute_command('echo "hello lab"')
        self.assertTrue(result["ok"])
        self.assertEqual(result["output"], "hello lab")

    def test_unknown_command_is_rejected(self) -> None:
        result = execute_command("uname -a")
        self.assertFalse(result["ok"])
        self.assertIn("unsupported command", str(result["output"]))

    def test_extra_args_are_rejected(self) -> None:
        result = execute_command("hostname extra")
        self.assertFalse(result["ok"])

    def test_capabilities_are_explicit(self) -> None:
        allowed = capabilities()
        self.assertIn("ping", allowed)
        self.assertIn("exit", allowed)
        self.assertNotIn("shell", allowed)
        self.assertEqual(len(allowed), len(set(allowed)))

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
