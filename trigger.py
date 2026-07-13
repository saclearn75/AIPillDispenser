"""Dispense trigger. Placeholder — real details come later.

Fires after answers are stored. Set TRIGGER_URL to POST the payload
somewhere; leave unset to just log. Swap the body when you get the real
trigger spec (GPIO call, device HTTP endpoint, etc.).
"""
import os

import httpx

_TRIGGER_URL = os.getenv("TRIGGER_URL")


def fire(payload: dict):
    """Runs in a FastAPI BackgroundTask (non-blocking)."""
    if not _TRIGGER_URL:
        print(f"[trigger] (no TRIGGER_URL) would dispense: {payload}")
        return
    try:
        httpx.post(_TRIGGER_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"[trigger] POST failed: {e}")
