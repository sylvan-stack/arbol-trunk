"""What is handed to `run` (RCT-0, "What is handed to a Trunk").

The launcher hands a Build `--root <root>` followed by the command and every later argument unchanged:

    --root <root> run [--request <file>] [--exchange <id>] [--chat <id>] [--replaces <id>] [--cwd <folder>]
                      [--driver <d>] [--subscription <s>] [--model <m>] [--effort <e>] [--detach] ["<message>"]

Short values are options; anything long is in the request file, read once. An option given beside the request file
replaces that field of the file, and `--driver`, `--subscription`, `--model` and `--effort` each replace only their own
field of `route`.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any

from .errors import invalid

ROOT_IDENTIFIER = re.compile(r"[a-z0-9]+", re.ASCII)
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.ASCII)
ROUTE_OPTIONS = {"--driver": "driver", "--subscription": "subscription", "--model": "model", "--effort": "effort"}
VALUE_OPTIONS = ("--request", "--exchange", "--chat", "--replaces", "--cwd", *ROUTE_OPTIONS)
FLAG_OPTIONS = ("--detach",)


@dataclass(frozen=True)
class Command:
    """The command line of `run`, as it was given."""

    root: str
    options: dict[str, str] = field(default_factory=dict)
    detach: bool = False
    message: str | None = None


@dataclass(frozen=True)
class Handed:
    """Everything `run` was handed, from the options and the request file together (RCT-0, StartRequest)."""

    root: str
    exchange: str | None
    chat: str | None
    replaces: str | None
    message: str | None
    route: dict[str, str]
    small_call_route: dict[str, Any] | None
    working_folder: str
    detach: bool


def parse(args: list[str]) -> Command:
    """`--root <root>` first, then `run`, its options and the message as the last argument."""
    if len(args) < 2 or args[0] != "--root":
        raise invalid("The Root is handed first, as --root <root>.")
    root = args[1]
    if not ROOT_IDENTIFIER.fullmatch(root):
        raise invalid(f"A Root identifier is one lower-case word of letters and digits, not {root!r}.")
    rest = args[2:]
    if not rest:
        raise invalid("No command was given: run.")
    if rest[0] != "run":
        raise invalid(f"Unknown command: {rest[0]}.")
    options: dict[str, str] = {}
    detach = False
    message: str | None = None
    index = 1
    while index < len(rest):
        arg = rest[index]
        name, equals, given = arg.partition("=")
        if name == "--root":
            raise invalid("The Root is handed once, as --root before the command.")
        if name in FLAG_OPTIONS and not equals:
            detach = True
        elif name in VALUE_OPTIONS:
            if equals:
                value = given
            else:
                index += 1
                if index >= len(rest):
                    raise invalid(f"{name} needs a value.")
                value = rest[index]
            if name in options:
                raise invalid(f"{name} is given twice.")
            options[name] = value
        elif arg.startswith("--") or arg == "-v":
            raise invalid(f"Unknown option: {arg}.")
        elif index == len(rest) - 1:
            message = arg
        else:
            raise invalid(f"Unexpected argument: {arg}. The message is the last argument.")
        index += 1
    return Command(root, options, detach, message)


def read_request(file: str) -> dict[str, Any]:
    """The request file, read once (RCT-0)."""
    try:
        with open(file, encoding="utf-8") as stream:
            value = json.load(stream)
    except OSError as error:
        raise invalid(f"The request file {file} cannot be read: {error.strerror}.") from None
    except ValueError:
        raise invalid(f"The request file {file} holds no JSON.") from None
    if not isinstance(value, dict):
        raise invalid(f"The request file {file} holds no JSON object.")
    return value


def handed(command: Command, started_in: str | None = None) -> Handed:
    """The options and the request file together: an option replaces only its own field of the file."""
    request: dict[str, Any] = read_request(command.options["--request"]) if "--request" in command.options else {}
    options = command.options

    def text(name: str, option: str) -> str | None:
        value = options.get(option, request.get(name))
        if value is not None and not isinstance(value, str):
            raise invalid(f"{name} is a string.")
        return value

    def identifier(name: str, option: str) -> str | None:
        value = text(name, option)
        if value is not None and not UUID.fullmatch(value):
            raise invalid(f"{name} is a UUID written in lower case with hyphens, not {value!r}.")
        return value

    route = request.get("route", {})
    if not isinstance(route, dict) or not all(isinstance(value, str) for value in route.values()):
        raise invalid("route is an object of strings.")
    route = dict(route)
    for option, name in ROUTE_OPTIONS.items():
        if option in options:
            route[name] = options[option]
    small_call_route = request.get("smallCallRoute")
    if small_call_route is not None and not isinstance(small_call_route, dict):
        raise invalid("smallCallRoute is an object.")
    message = command.message if command.message is not None else request.get("message")
    if message is not None and not isinstance(message, str):
        raise invalid("message is a string.")
    folder = text("workingFolder", "--cwd")
    if folder is None:
        folder = started_in if started_in is not None else os.getcwd()
    if not os.path.isabs(folder) or not os.path.isdir(folder):
        raise invalid(f"The working folder is an absolute path to a folder that exists, not {folder!r}.")
    return Handed(root=command.root, exchange=identifier("exchange", "--exchange"), chat=identifier("chat", "--chat"),
                  replaces=identifier("replaces", "--replaces"), message=message, route=route,
                  small_call_route=small_call_route, working_folder=folder, detach=command.detach)
