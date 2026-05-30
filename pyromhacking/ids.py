"""Converters from pyromhacking models to flat ``str -> str`` external-ID dicts.

Each converter returns a flat ``str -> str`` dict of namespaced external IDs
(canonical anchor key ``<site>_id``) for cross-referencing entities across data
sources.

The canonical anchor is the pair (``romhacking_section``, ``romhacking_id``):
together they uniquely identify an entry, since the numeric id space is shared
across all four sections (``/hacks/1/`` and ``/translations/1/`` are different
entries). A flat ``romhacking_<section>_id`` key is also written so a consumer
can join on a single field per section.

Keys are namespaced ``romhacking_*``.

Key namespaces
--------------
Common (every entry):
    ``romhacking_id``            — numeric entry id
    ``romhacking_section``       — hacks | translations | utilities | documents
    ``romhacking_<section>_id``  — canonical per-section anchor (e.g. ``romhacking_hacks_id``)
    ``romhacking_url``           — canonical entry URL
    ``romhacking_title``
    ``romhacking_game``
    ``romhacking_system``        — console / platform
    ``romhacking_category``
    ``romhacking_version``
    ``romhacking_authors``       — comma-joined
    ``romhacking_release_date``
    ``romhacking_rating``        — float as str
    ``romhacking_downloads``     — int as str

Hack adds:
    ``romhacking_hack_type`` / ``romhacking_genre``
Translation adds:
    ``romhacking_language`` / ``romhacking_genre`` / ``romhacking_published_by``
Utility adds:
    ``romhacking_os`` / ``romhacking_language``
Document adds:
    ``romhacking_document_type`` / ``romhacking_language``
"""
from __future__ import annotations

import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pyromhacking.models import Document, Hack, Translation, Utility, _Entry

BASE_URL = "https://www.romhacking.net"
_SECTIONS = ("hacks", "translations", "utilities", "documents")
_ID_RE = re.compile(r"/(hacks|translations|utilities|documents)/(\d+)")


def entry_url(section: str, entry_id: str) -> str:
    """Canonical romhacking.net URL for a (section, id) pair."""
    return f"{BASE_URL}/{section}/{entry_id}/"


def parse_ref(url: str):
    """Pull ``(section, id)`` out of a romhacking.net entry URL, or ``None``."""
    if not url:
        return None
    m = _ID_RE.search(url)
    if not m:
        return None
    return m.group(1), m.group(2)


def _base_extra(entry: "_Entry") -> dict:
    section = entry.section
    extra: dict = {
        "romhacking_id": str(entry.id),
        "romhacking_section": section,
        "romhacking_url": entry.url or entry_url(section, entry.id),
    }
    if section in _SECTIONS:
        extra[f"romhacking_{section}_id"] = str(entry.id)
    if entry.title:
        extra["romhacking_title"] = entry.title
    if entry.game:
        extra["romhacking_game"] = entry.game
    if entry.system:
        extra["romhacking_system"] = entry.system
    if entry.category:
        extra["romhacking_category"] = entry.category
    if entry.version:
        extra["romhacking_version"] = entry.version
    if entry.authors:
        extra["romhacking_authors"] = ", ".join(entry.authors)
    if entry.release_date:
        extra["romhacking_release_date"] = entry.release_date
    if entry.rating is not None:
        extra["romhacking_rating"] = str(entry.rating)
    if entry.downloads is not None:
        extra["romhacking_downloads"] = str(entry.downloads)
    return extra


def hack_to_extra(hack: "Hack") -> dict:
    """Convert a :class:`~pyromhacking.models.Hack` to a flat external-ID dict."""
    extra = _base_extra(hack)
    if hack.hack_type:
        extra["romhacking_hack_type"] = hack.hack_type
    if hack.genre:
        extra["romhacking_genre"] = hack.genre
    return extra


def translation_to_extra(translation: "Translation") -> dict:
    """Convert a :class:`~pyromhacking.models.Translation` to a flat external-ID dict."""
    extra = _base_extra(translation)
    if translation.language:
        extra["romhacking_language"] = translation.language
    if translation.genre:
        extra["romhacking_genre"] = translation.genre
    if translation.published_by:
        extra["romhacking_published_by"] = translation.published_by
    return extra


def utility_to_extra(utility: "Utility") -> dict:
    """Convert a :class:`~pyromhacking.models.Utility` to a flat external-ID dict."""
    extra = _base_extra(utility)
    if utility.os:
        extra["romhacking_os"] = utility.os
    if utility.language:
        extra["romhacking_language"] = utility.language
    return extra


def document_to_extra(document: "Document") -> dict:
    """Convert a :class:`~pyromhacking.models.Document` to a flat external-ID dict."""
    extra = _base_extra(document)
    if document.document_type:
        extra["romhacking_document_type"] = document.document_type
    if document.language:
        extra["romhacking_language"] = document.language
    return extra


_CONVERTERS = {
    "hacks": hack_to_extra,
    "translations": translation_to_extra,
    "utilities": utility_to_extra,
    "documents": document_to_extra,
}


def entry_to_extra(entry: "_Entry") -> dict:
    """Dispatch to the converter for ``entry.section``."""
    fn = _CONVERTERS.get(entry.section)
    if fn is None:
        return _base_extra(entry)
    return fn(entry)
