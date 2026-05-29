"""Offline tests for ``ExternalIds.extra`` converters and ref parsing."""
from pyromhacking._parse import parse_hack, parse_translation
from pyromhacking.ids import (
    entry_to_extra,
    entry_url,
    hack_to_extra,
    parse_ref,
    translation_to_extra,
)


def test_entry_url():
    assert entry_url("hacks", "1") == "https://www.romhacking.net/hacks/1/"


def test_parse_ref():
    assert parse_ref("https://www.romhacking.net/hacks/42/") == ("hacks", "42")
    assert parse_ref("/translations/7/") == ("translations", "7")
    assert parse_ref("https://example.com/") is None
    assert parse_ref("") is None


def test_hack_to_extra_anchor(hack_html):
    hack = parse_hack(hack_html, "1")
    extra = hack_to_extra(hack)
    assert extra["romhacking_id"] == "1"
    assert extra["romhacking_section"] == "hacks"
    assert extra["romhacking_hacks_id"] == "1"  # canonical per-section anchor
    assert extra["romhacking_system"] == "NES"
    assert extra["romhacking_downloads"] == "6523"
    assert extra["romhacking_authors"] == "Sliver X"
    assert all(k.startswith("romhacking_") for k in extra)


def test_translation_to_extra(translation_html):
    tr = parse_translation(translation_html, "1")
    extra = translation_to_extra(tr)
    assert extra["romhacking_translations_id"] == "1"
    assert extra["romhacking_language"] == "English"
    assert extra["romhacking_published_by"] == "ASCII"


def test_entry_to_extra_dispatch(hack_html):
    hack = parse_hack(hack_html, "1")
    assert entry_to_extra(hack) == hack_to_extra(hack)
