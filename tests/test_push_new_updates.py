"""Tests for the deploy-time "What's new" notification builder."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import push_new_updates as push

CORRECTION = {
    "date": "2026-10-08",
    "kind": "correction",
    "title": "Correction: Celina Bohrer died on 19 February 1977",
    "title_pt": "Correção: Celina Bohrer morreu em 19 de fevereiro de 1977",
}
MILESTONE = {"date": "2026-10-08", "kind": "milestone", "title": "A new record", "title_pt": "Um novo registro"}
DOCUMENT = {"date": "2026-10-08", "kind": "document", "title": "1891 birth", "primary": "CIV-0045"}
OLDER = {"date": "2026-09-24", "kind": "milestone", "title": "Older news", "title_pt": "Notícia antiga"}


def feed(*entries: dict) -> dict:
    return {"generated": "x", "updates": list(entries)}


class BuildPayloadTests(unittest.TestCase):
    def test_nothing_new_sends_nothing(self) -> None:
        self.assertIsNone(push.build_payload(feed(OLDER), feed(OLDER)))

    def test_documents_alone_do_not_trigger_a_notification(self) -> None:
        self.assertIsNone(push.build_payload(feed(OLDER), feed(DOCUMENT, OLDER)))

    def test_one_summary_for_several_new_entries(self) -> None:
        payload = push.build_payload(feed(OLDER), feed(CORRECTION, MILESTONE, DOCUMENT, OLDER))
        self.assertIsNotNone(payload)
        self.assertEqual(payload["counts"], {"updates": 2, "documents": 1})
        self.assertEqual(payload["title"]["pt"], "Quatro Rios — novidades")
        self.assertEqual(
            payload["body"]["en"],
            "Correction: Celina Bohrer died on 19 February 1977 (+1 more update · +1 new document)",
        )
        self.assertEqual(
            payload["body"]["pt"],
            "Correção: Celina Bohrer morreu em 19 de fevereiro de 1977 (+1 novidade · +1 novo documento)",
        )
        self.assertEqual(payload["url"], "./?open=updates")
        self.assertEqual(payload["tag"], "whats-new")

    def test_rewording_or_redating_an_old_entry_is_not_news(self) -> None:
        reworded = dict(OLDER, title="Older news, reworded", title_pt="Notícia antiga, reescrita")
        self.assertIsNone(push.build_payload(feed(MILESTONE, OLDER), feed(MILESTONE, reworded)))
        redated = dict(OLDER, date="2026-09-30")
        self.assertIsNone(push.build_payload(feed(MILESTONE, OLDER), feed(MILESTONE, redated)))

    def test_rewording_the_newest_entry_with_replaces_is_not_news(self) -> None:
        reworded = dict(CORRECTION, title="Correction, widened", title_pt="Correção, ampliada", replaces=CORRECTION["title"])
        self.assertIsNone(push.build_payload(feed(CORRECTION, OLDER), feed(reworded, OLDER)))
        unmarked = dict(reworded)
        del unmarked["replaces"]
        self.assertIsNotNone(push.build_payload(feed(CORRECTION, OLDER), feed(unmarked, OLDER)), "without replaces it reads as a same-day addition")

    def test_a_same_day_addition_after_an_earlier_deploy_is_news(self) -> None:
        payload = push.build_payload(feed(MILESTONE, OLDER), feed(CORRECTION, MILESTONE, OLDER))
        self.assertEqual(payload["counts"], {"updates": 1, "documents": 0})

    def test_a_retitled_document_is_not_counted_again(self) -> None:
        retitled = dict(DOCUMENT, title="1891 civil birth, retitled")
        payload = push.build_payload(feed(DOCUMENT, OLDER), feed(CORRECTION, retitled, OLDER))
        self.assertEqual(payload["counts"]["documents"], 0)

    def test_malformed_entries_are_ignored(self) -> None:
        payload = push.build_payload({"updates": ["junk", None, OLDER]}, {"updates": [CORRECTION, 7, OLDER]})
        self.assertEqual(payload["counts"]["updates"], 1)

    def test_the_payload_has_a_stable_id_for_safe_retries(self) -> None:
        first = push.build_payload(feed(OLDER), feed(CORRECTION, OLDER))
        second = push.build_payload(feed(OLDER), feed(CORRECTION, OLDER))
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(len(first["id"]), 20)

    def test_long_headlines_are_shortened(self) -> None:
        long_entry = dict(MILESTONE, title="x" * 400, title_pt="y" * 400)
        payload = push.build_payload(feed(), feed(long_entry))
        self.assertLessEqual(len(payload["body"]["en"]), push.MAX_HEADLINE)
        self.assertTrue(payload["body"]["en"].endswith("…"))

    def test_cli_writes_nothing_when_the_live_feed_is_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            new = Path(tmp) / "new.json"
            new.write_text(json.dumps(feed(CORRECTION)), encoding="utf-8")
            out = Path(tmp) / "payload.json"
            code = push.main(["--old", str(Path(tmp) / "missing.json"), "--new", str(new), "--write", str(out)])
            self.assertEqual(code, 0)
            self.assertFalse(out.exists())

    def test_cli_writes_the_payload_when_there_is_news(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old, new, out = (Path(tmp) / name for name in ("old.json", "new.json", "payload.json"))
            old.write_text(json.dumps(feed(OLDER)), encoding="utf-8")
            new.write_text(json.dumps(feed(CORRECTION, OLDER)), encoding="utf-8")
            push.main(["--old", str(old), "--new", str(new), "--write", str(out)])
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["counts"]["updates"], 1)


if __name__ == "__main__":
    unittest.main()
