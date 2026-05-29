"""Offline parsing tests against captured romhacking.net fixtures."""
import pytest

from pyromhacking._parse import (
    NotFoundError,
    is_error_page,
    parse_hack,
    parse_listing,
    parse_translation,
    _soup,
)
from pyromhacking.models import Hack, Translation


def test_parse_hack_core_fields(hack_html):
    hack = parse_hack(hack_html, "1")
    assert isinstance(hack, Hack)
    assert hack.id == "1"
    assert hack.section == "hacks"
    assert hack.title == "Dragoon X Omega - Gold Edition"
    assert hack.game == "Dragon Warrior"
    assert hack.system == "NES"
    assert hack.console == "NES"
    assert hack.category == "Complete"
    assert hack.version == "2.0f"
    assert hack.genre == "Role Playing"
    assert hack.authors == ["Sliver X"]
    assert hack.release_date == "20 January 2003"
    assert hack.last_modified == "07 October 2015"
    assert hack.downloads == 6523
    assert hack.url == "https://www.romhacking.net/hacks/1/"


def test_parse_hack_description_and_credits(hack_html):
    hack = parse_hack(hack_html, "1")
    assert hack.description.startswith("A nation just over a rebellion")
    assert hack.credits
    assert hack.credits[0].contributor == "Sliver X"
    assert hack.files
    assert any("/download/" in f.url for f in hack.files)
    assert hack.images  # screenshots present


def test_parse_translation_fields(translation_html):
    tr = parse_translation(translation_html, "1")
    assert isinstance(tr, Translation)
    assert tr.title == "Namida no Soukoban Special"
    assert tr.game == "Namida no Soukoban Special"
    assert tr.language == "English"
    assert tr.system == "Famicom Disk System"
    assert tr.status == "Fully Playable"
    assert tr.published_by == "ASCII"
    assert tr.downloads == 1524


def test_parse_listing_ids(listing_html):
    ids = parse_listing(listing_html, "hacks")
    assert len(ids) >= 10
    assert all(i.isdigit() for i in ids)
    assert len(set(ids)) == len(ids)  # deduped


def test_entry_not_found():
    html = "<html><body><div class='topbar'><h2>Error Encountered!</h2></div></body></html>"
    assert is_error_page(_soup(html))
    with pytest.raises(NotFoundError):
        parse_hack(html, "999999999")


def test_real_page_is_not_error(hack_html):
    assert not is_error_page(_soup(hack_html))


def test_as_dict_roundtrip(hack_html):
    hack = parse_hack(hack_html, "1")
    d = hack.as_dict
    assert d["title"] == hack.title
    assert d["hack_type"] == hack.hack_type
    assert d["downloads"] == 6523
    assert isinstance(d["files"], list)
