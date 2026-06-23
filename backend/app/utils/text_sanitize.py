"""Plain-text cleanup for LLM outputs shown without a markdown renderer."""

from __future__ import annotations

import re

_HEADING = re.compile(r"^#{1,6}\s*", re.MULTILINE)
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_CODE = re.compile(r"`([^`]+)`")
_STRAY = re.compile(r"[#*]+")


def sanitize_mentor_reply(text: str) -> str:
    """Strip common markdown markers while keeping readable plain text."""
    if not text:
        return text
    cleaned = _HEADING.sub("", text)
    cleaned = _BOLD.sub(r"\1", cleaned)
    cleaned = _ITALIC.sub(r"\1", cleaned)
    cleaned = _CODE.sub(r"\1", cleaned)
    cleaned = _STRAY.sub("", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
