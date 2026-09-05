"""Safe, allowlisted commands for the local C2 lab simulator."""

from __future__ import annotations

import getpass
import os
import platform as platform_module
import shlex
import socket
import sys
from datetime import datetime, timezone
from typing import Callable

VERSION = "2.1.0"
MAX_COMMAND_LENGTH = 512
MAX_ECHO_LENGTH = 256

_SIMPLE_COMMANDS: dict[str, Callable[[], str]] = {
    "ping": lambda: "pong",
    "hostname": socket.gethostname,
    "whoami": getpass.getuser,
    "cwd": os.getcwd,
    "platform": platform_module.platform,
    "python": platform_module.python_version,
    "time": lambda: datetime.now(timezone.utc).isoformat(),
}

_HELP = """Available commands:
  help                 Show this help
  ping                 Check agent responsiveness
  hostname             Show local hostname
  whoami                Show current local user
  cwd                   Show current working directory
  platform              Show platform information
  python                Show Python version
  time                  Show current UTC time
  echo <text>           Return supplied text (max 256 characters)
  exit                  Close the lab session

This simulator intentionally does not execute arbitrary system commands.
"""


def execute_command(command_line: str) -> dict[str, object]:
    """Execute one allowlisted lab command and return a structured result."""
    if not isinstance(command_line, str):
        return _result(False, "", "command must be a string")

    command_line = command_line.strip()
    if not command_line:
        return _result(False, "", "empty command")
    if len(command_line) > MAX_COMMAND_LENGTH:
        return _result(
            False,
            "",
            f"command exceeds {MAX_COMMAND_LENGTH} characters",
        )
    if "\x00" in command_line:
        return _result(False, "", "command contains a NUL byte")

    try:
        parts = shlex.split(command_line)
    except ValueError as exc:
        return _result(False, "", f"parse error: {exc}")

    if not parts:
        return _result(False, "", "empty command")

    name = parts[0].lower()
    args = parts[1:]

    if name == "help":
        if args:
            return _result(False, name, "help takes no arguments")
        return _result(True, name, _HELP.rstrip())

    if name == "echo":
        text = " ".join(args)
        if len(text) > MAX_ECHO_LENGTH:
            return _result(
                False,
                name,
                f"echo text exceeds {MAX_ECHO_LENGTH} characters",
            )
        return _result(True, name, text)

    if name == "exit":
        if args:
            return _result(False, name, "exit takes no arguments")
        return _result(True, name, "session closing")

    handler = _SIMPLE_COMMANDS.get(name)
    if handler is None:
        return _result(
            False,
            name,
            f"unsupported command: {name}. Type 'help' for the allowlist.",
        )
    if args:
        return _result(False, name, f"{name} takes no arguments")

    try:
        return _result(True, name, handler())
    except OSError as exc:
        return _result(False, name, f"command failed: {exc}")


def capabilities() -> list[str]:
    """Return the explicit simulator command allowlist."""
    return [
        "help",
        "ping",
        "hostname",
        "whoami",
        "cwd",
        "platform",
        "python",
        "time",
        "echo",
        "exit",
    ]


def agent_metadata() -> dict[str, object]:
    """Return metadata used by the local lab handshake."""
    return {
        "hostname": socket.gethostname(),
        "user": getpass.getuser(),
        "platform": platform_module.system(),
        "python": platform_module.python_version(),
        "pid": os.getpid(),
        "simulator_version": VERSION,
        "capabilities": capabilities(),
        "executable": os.path.basename(sys.executable),
    }


def _result(ok: bool, command: str, output: str) -> dict[str, object]:
    return {
        "type": "result",
        "ok": ok,
        "command": command,
        "output": output,
    }
