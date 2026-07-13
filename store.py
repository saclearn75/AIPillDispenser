"""Answer storage — appends one JSON line per answer to answers.jsonl.

(HydraDB was dropped; JSONL is the store now.) To move to SQLite/Postgres
later, swap the body of store_answer — nothing else changes.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# next to this file, so it's predictable regardless of the server's cwd
_LOG = Path(os.getenv("ANSWERS_LOG") or Path(__file__).parent / "answers.jsonl")


def store_answer(record: dict):
    """Append one answer. Runs in a FastAPI BackgroundTask (non-blocking)."""
    record = dict(record)
    record.setdefault("stored_at", datetime.now(timezone.utc).isoformat())
    with _LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
