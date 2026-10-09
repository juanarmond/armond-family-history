#!/usr/bin/env python3
"""Build, and optionally send, the single "What's new" push notification for a deploy.

The deploy workflow compares the feed readers can see now (the live ``updates.json``)
with the one about to be published. If the new feed adds at least one curated entry
(a milestone, correction or new person), it writes ONE bilingual summary: the newest
curated headline, how many more updates came with it, and how many new documents.
Routine document additions never trigger a notification on their own; they only add
"+N new documents" to a summary. After the deploy, ``--send`` posts the summary to the
family-notify Worker, page by page.

Usage:
  push_new_updates.py --old live.json --new _site/updates.json --write payload.json
  push_new_updates.py --send payload.json     # needs NOTIFY_ENDPOINT and NOTIFY_TOKEN
  push_new_updates.py --test                  # one test notification to every device

Standard library only, so the deploy job can run it without installing anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SITE_NAME = "Quatro Rios"
MAX_HEADLINE = 140
TEST_PAYLOAD = {
    "title": {"en": f"{SITE_NAME} — test", "pt": f"{SITE_NAME} — teste"},
    "body": {"en": "Notifications are working on this device.", "pt": "As notificações estão funcionando neste aparelho."},
    "url": "./?open=updates",
    "tag": "whats-new-test",
}


def entry_key(entry: dict[str, Any]) -> tuple[Any, ...]:
    return (entry.get("date"), entry.get("kind"), entry.get("title"), entry.get("primary"))


def _entries(feed: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry for entry in feed.get("updates") or [] if isinstance(entry, dict)]


def _is_document(entry: dict[str, Any]) -> bool:
    return (entry.get("kind") or "document") == "document"


def new_curated(old: dict[str, Any], new: dict[str, Any]) -> list[dict[str, Any]]:
    """Curated entries that are genuinely new.

    Curated entries carry no stable id, so "new" means: not already live AND dated no earlier
    than the newest curated entry already live. Rewording or re-dating an older entry (which
    keeps or lowers its date) therefore never re-announces it; a same-day addition still counts.
    Rewording the newest entry looks like a same-day addition, so such an entry lists the titles
    it went out under in ``replaces`` (one title or a list) and is recognised as already live.
    """
    live = [entry for entry in _entries(old) if not _is_document(entry)]
    seen = {entry_key(entry) for entry in live}
    newest = max((str(entry.get("date") or "") for entry in live), default="")

    def already_live(entry: dict[str, Any]) -> bool:
        replaced = entry.get("replaces") or []
        earlier = [replaced] if isinstance(replaced, str) else [title for title in replaced if isinstance(title, str)]
        return any(entry_key({**entry, "title": title}) in seen for title in [entry.get("title"), *earlier])

    return [
        entry for entry in _entries(new)
        if not _is_document(entry) and not already_live(entry) and str(entry.get("date") or "") >= newest
    ]


def new_documents(old: dict[str, Any], new: dict[str, Any]) -> list[dict[str, Any]]:
    """Documents whose record (primary id) is not live yet; a retitled document is not new."""
    def ident(entry: dict[str, Any]) -> Any:
        return entry.get("primary") or entry_key(entry)
    seen = {ident(entry) for entry in _entries(old) if _is_document(entry)}
    return [entry for entry in _entries(new) if _is_document(entry) and ident(entry) not in seen]


def _shorten(text: str) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= MAX_HEADLINE else text[: MAX_HEADLINE - 1].rstrip() + "…"


def _plural(count: int, one: str, many: str) -> str:
    return (one if count == 1 else many).format(n=count)


def build_payload(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any] | None:
    """Return the notification for this deploy, or None when there is nothing to announce."""
    curated = new_curated(old, new)
    documents = new_documents(old, new)
    if not curated:
        return None

    lead = curated[0]
    more = len(curated) - 1
    body_en = _shorten(lead.get("title"))
    body_pt = _shorten(lead.get("title_pt") or lead.get("title"))
    extras_en, extras_pt = [], []
    if more:
        extras_en.append(_plural(more, "+{n} more update", "+{n} more updates"))
        extras_pt.append(_plural(more, "+{n} novidade", "+{n} novidades"))
    if documents:
        extras_en.append(_plural(len(documents), "+{n} new document", "+{n} new documents"))
        extras_pt.append(_plural(len(documents), "+{n} novo documento", "+{n} novos documentos"))
    if extras_en:
        body_en = f"{body_en} ({' · '.join(extras_en)})"
        body_pt = f"{body_pt} ({' · '.join(extras_pt)})"

    title = {"en": f"{SITE_NAME} — what's new", "pt": f"{SITE_NAME} — novidades"}
    body = {"en": body_en, "pt": body_pt}
    # The id lets the Worker skip pages it already sent if a failed deploy is re-run.
    message_id = hashlib.sha256(json.dumps([title, body], ensure_ascii=False).encode("utf-8")).hexdigest()[:20]
    return {
        "id": message_id,
        "title": title,
        "body": body,
        "url": "./?open=updates",
        "tag": "whats-new",
        "counts": {"updates": len(curated), "documents": len(documents)},
    }


def send(payload: dict[str, Any], endpoint: str, token: str) -> dict[str, int]:
    """POST the payload to the Worker's /notify, following its pagination cursor."""
    totals = {"sent": 0, "removed": 0, "failed": 0}
    cursor = None
    for _ in range(1000):  # a hard stop far above any realistic subscriber count
        body = {key: payload[key] for key in ("id", "title", "body", "url", "tag") if key in payload}
        if cursor:
            body["cursor"] = cursor
        request = urllib.request.Request(
            endpoint.rstrip("/") + "/notify",
            data=json.dumps(body).encode("utf-8"),
            # Cloudflare rejects Python's default "Python-urllib" user agent (error 1010).
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "quatro-rios-notify/1.0 (+https://juanarmond.github.io/armond-family-history/)",
            },
            method="POST",
        )
        result = _post_with_retries(request)
        for key in totals:
            totals[key] += int(result.get(key) or 0)
        cursor = result.get("cursor")
        if not cursor:
            break
    return totals


def _post_with_retries(request: urllib.request.Request, attempts: int = 3) -> dict[str, Any]:
    """POST, retrying transient failures (network errors, 429, 5xx). Retrying is safe: the
    Worker skips any page it already sent for the same message id."""
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if (error.code != 429 and error.code < 500) or attempt == attempts:
                raise
        except urllib.error.URLError:
            if attempt == attempts:
                raise
        time.sleep(3 * attempt)
    raise RuntimeError("unreachable")


def _load(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--old", type=Path, help="the live updates.json readers see now")
    parser.add_argument("--new", type=Path, help="the updates.json about to be deployed")
    parser.add_argument("--write", type=Path, help="write the payload here (only when there is one)")
    parser.add_argument("--send", type=Path, help="send a payload written earlier")
    parser.add_argument("--test", action="store_true", help="send a test notification to every subscribed device")
    args = parser.parse_args(argv)

    if args.send or args.test:
        payload = TEST_PAYLOAD if args.test else _load(args.send)
        endpoint = os.environ.get("NOTIFY_ENDPOINT", "")
        token = os.environ.get("NOTIFY_TOKEN", "")
        if not payload or not endpoint or not token:
            print("No payload or notification secrets; nothing sent.")
            return 0
        totals = send(payload, endpoint, token)
        print(f"Notification sent: {totals['sent']} delivered, {totals['removed']} expired "
              f"subscriptions removed, {totals['failed']} failed.")
        return 0

    if not args.old or not args.new:
        parser.error("--old and --new are required unless --send is given")
    old, new = _load(args.old), _load(args.new)
    if old is None or new is None:
        # Without the live feed we cannot tell what is new; never announce the whole history.
        print("A feed could not be read; no notification will be sent.")
        return 0
    payload = build_payload(old, new)
    if payload is None:
        print("No new curated entries; no notification will be sent.")
        return 0
    print(f"Notification prepared: {payload['counts']['updates']} update(s), "
          f"{payload['counts']['documents']} document(s).\n  EN: {payload['body']['en']}\n  PT: {payload['body']['pt']}")
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
