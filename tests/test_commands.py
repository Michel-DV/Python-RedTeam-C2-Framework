from __future__ import annotations

import unittest

from commands import capabilities, execute_command


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


if __name__ == "__main__":
    unittest.main()
