"""Accepted chat ownership crosses the actual Trunk/Driver process boundary (ARC-4.7)."""

import json
import os
import uuid

from stand_ins import with_capabilities
from test_run import LAUNCHER, WholeExchange


class ChatIdentity(WholeExchange):
    def test_accepted_chat_survives_continuation_replacement_and_driver_selection(self) -> None:
        settings = self.home / ".arbol/arbol-trunk/trivial.json"
        settings.parent.mkdir(parents=True)
        settings.write_text(json.dumps({"driver": "claude"}))
        for driver in ("codex", "pi", "mimo"):
            script = with_capabilities(LAUNCHER).replace('"driver":"claude"', f'"driver":"{driver}"')
            entry = self.bin / f"arbol-{driver}-driver"
            entry.write_text(script)
            os.chmod(entry, 0o700)

        chat = ""
        previous = ""
        # One accepted chat crosses default selection, explicit selection and replacement.
        # Pi/MiMo's strict parsers must never receive either Arbol identity marker.
        for index, driver in enumerate(("claude", "codex", "pi", "mimo"), 1):
            exchange = str(uuid.uuid4())
            args = ["--exchange", exchange]
            if index > 1:
                args += ["--driver", driver]
            if index == 2:
                args += ["--chat", chat]
            elif index > 2:
                args += ["--replaces", previous]
            status, lines = self.run_trunk(*args, *(["answer"] if index <= 2 else []))
            self.assertEqual(status, 0, lines)
            accepted = json.loads(lines[0])
            self.assertTrue(accepted["accepted"])
            if index == 1:
                chat = accepted["chat"]
                self.assertEqual(str(uuid.UUID(chat)), chat)
            self.assertEqual(accepted["chat"], chat)
            self.assertEqual(self.database.exchanges[exchange].chat, chat)
            observed = json.loads((self.log / f"request-{index}.json").read_text())
            self.assertEqual(observed["chatSessionId"], accepted["chat"])
            self.assertNotIn("rootId", observed)
            if driver in {"claude", "codex"}:
                self.assertIs(observed["arbolChat"], True)
            else:
                self.assertNotIn("arbolChat", observed)
            previous = exchange
