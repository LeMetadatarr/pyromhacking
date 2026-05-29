"""String-cleaning helpers for scraped romhacking.net content."""
from __future__ import annotations

import html
import re
import unicodedata
from typing import List, Optional


def clean(text: str) -> str:
    """Unescape HTML entities, normalise, collapse whitespace, strip."""
    if not text:
        return ""
    text = html.unescape(text)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_or_none(text: str) -> Optional[str]:
    """Like :func:`clean` but returns ``None`` for empty / placeholder values."""
    val = clean(text)
    if not val or val.lower() in ("none", "no data", "n/a", "-", "unknown"):
        return None
    return val


def clean_multiline(text: str) -> str:
    """Unescape and normalise but keep paragraph breaks (double newlines)."""
    if not text:
        return ""
    text = html.unescape(text)
    text = unicodedata.normalize("NFKC", text)
    # collapse intra-line whitespace, preserve blank-line paragraph breaks
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    out: List[str] = []
    blank = False
    for ln in lines:
        if ln:
            out.append(ln)
            blank = False
        elif not blank and out:
            out.append("")
            blank = True
    return "\n".join(out).strip()


def parse_int(raw: str) -> Optional[int]:
    """Extract the first integer from a string ('6,523' → 6523)."""
    if not raw:
        return None
    m = re.search(r"-?\d[\d,]*", raw)
    if not m:
        return None
    try:
        return int(m.group(0).replace(",", ""))
    except ValueError:
        return None


def parse_float(raw: str) -> Optional[float]:
    """Extract the first decimal number from a string ('9.2 / 10' → 9.2)."""
    if not raw:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", raw)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


_ID_RE = re.compile(r"/(?:hacks|translations|utilities|documents|community|games)/(\d+)")


def id_from_url(url: str) -> Optional[str]:
    """Pull the numeric id out of a romhacking.net entity URL."""
    if not url:
        return None
    m = _ID_RE.search(url)
    return m.group(1) if m else None
