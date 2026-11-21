"""Generate a chat title independently of the Exchange that started it."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from threading import Thread

from .admission import Admission
from .build import BuildRecordError, Compatibility, build_info
from .database import DatabaseUnavailable, PostgresConnection, installed_postgres
from .errors import Refusal
from .phase_details import PhaseDetails
from .root import SECURITY, Installation, installation

MAX_WORDS = 12
MAX_TITLE_LENGTH = 240
NARRATOR_INPUT_BYTES = 192_000
# Allow the JSON-escaped source and the adapter's short instructions.
MODEL_INPUT_BYTES = 6 * NARRATOR_INPUT_BYTES + 4096
NARRATOR_TIMEOUT_SECONDS = 280  # Narrator allows at most 270 seconds, including a format retry.
WORKER = "--chat-title-worker"
MODEL = "--chat-title-model"


def narrator_launcher(home: Path) -> Path:
    return home / "Applications/Mycel/bin/mycel"


def model_launcher(home: Path) -> Path:
    return home / "Applications/Arbol/bin/arbol-codex-driver"


def entry_arguments(*arguments: str) -> list[str]:
    entry = Path(__file__).resolve().parents[2] / "bin/entry.py"
    return [sys.executable, "-I", "-B", str(entry), *arguments]


def launch(home: Path, details: PhaseDetails) -> None:
    """Start a bounded chat metadata job whose lifetime is independent of the Exchange."""
    arguments = entry_arguments(WORKER, details.exchange)
    cwd = str(home)
    try:
        if not all(os.access(path, os.X_OK) for path in (narrator_launcher(home), model_launcher(home))):
            return
        process = subprocess.Popen(arguments, cwd=cwd, start_new_session=True, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    except OSError:
        return
    details.subprocess(arguments, cwd)
    # Reap it while the Exchange is running without making Trunk shutdown wait.
    with suppress(RuntimeError):
        Thread(target=process.wait, daemon=True).start()


@asynccontextmanager
async def connection(context: Installation, compatibility: Compatibility, *,
                     generation: str | None = None) -> AsyncIterator[tuple[PostgresConnection, str]]:
    with Admission(context.runtime).lease("normal", generation=generation) as lease:
        connect = installed_postgres(context, SECURITY, compatibility, lease=lease)
        database = await connect()
        try:
            yield database, lease.state.generation
        finally:
            await database.close()


def label(home: Path, message: str) -> str | None:
    payload = message.encode("utf-8")
    if not message.strip() or len(payload) > NARRATOR_INPUT_BYTES:
        return None
    arguments = [str(narrator_launcher(home)), "narrator", "label", "--max-words", str(MAX_WORDS),
                 "--count-all-words", "--model-command", json.dumps(entry_arguments(MODEL))]
    result = subprocess.run(arguments, cwd=home, input=payload, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, timeout=NARRATOR_TIMEOUT_SECONDS, check=False)
    if result.returncode != 0:
        return None
    title, newline, rest = result.stdout.decode("utf-8").partition("\n")
    if (not newline or rest or len(title) > MAX_TITLE_LENGTH or not 1 <= len(title.split()) <= MAX_WORDS
            or not any(character.isalnum() for character in title) or "\0" in title):
        return None
    return title


async def run_worker(home: Path, exchange: str) -> int:
    try:
        build, compatibility = build_info()
        context = installation(home)
        if build == "0" and not context.target.socket:
            return 1
        async with connection(context, compatibility) as (database, generation):
            source = await database.chat_title_source(exchange)
        if source is not None:
            chat, message = source
            title = label(home, message)
            if title is not None:
                async with connection(context, compatibility, generation=generation) as (database, _):
                    await database.set_chat_title_if_untitled(chat, title)
    except (BuildRecordError, DatabaseUnavailable, Refusal, OSError, ValueError, subprocess.TimeoutExpired):
        return 1
    return 0


def run_model(home: Path) -> int:
    """Adapt the Narrator prompt to the existing tools-off Codex Driver route."""
    try:
        prompt = sys.stdin.buffer.read(MODEL_INPUT_BYTES + 1)
        if not 0 < len(prompt) <= MODEL_INPUT_BYTES:
            return 1
        request = {"input": prompt.decode("utf-8"), "tools": "none", "model": "gpt-6.2-sol", "effort": "medium"}
        payload = (json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8")
        return subprocess.run([str(model_launcher(home)), "run", "--request", "-", "--output", "text"],
                              input=payload, stderr=subprocess.DEVNULL, check=False).returncode
    except (OSError, ValueError):
        return 1
