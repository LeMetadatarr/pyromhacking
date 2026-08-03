"""Offline tests for listing pagination, id-walking, and entry fetch.

``list_ids``, ``iter_ids``, ``get_entry`` and ``iter_entries`` all go through
``pyromhacking.transport.get_html``; here that call is monkeypatched to
replay the real recorded fixtures under ``tests/fixtures/`` instead of
hitting the network, so pagination/resume behaviour is exercised without
FlareSolverr.
"""
import pytest

from pyromhacking import hacks
from pyromhacking._parse import NotFoundError, parse_listing_next_page
from pyromhacking.models import Hack


# ---- parse_listing_next_page ----------------------------------------------


def test_parse_listing_next_page_hacks(listing_html):
    assert parse_listing_next_page(listing_html) == 449


def test_parse_listing_next_page_no_links():
    assert parse_listing_next_page("<html><body>no pagination here</body></html>") is None


# ---- list_ids / iter_ids ---------------------------------------------------


def test_list_ids_single_page(monkeypatch, listing_html):
    calls = []

    def fake_get_html(path, params=None, **kwargs):
        calls.append(path)
        return listing_html

    monkeypatch.setattr(hacks.transport, "get_html", fake_get_html)
    ids = hacks.list_ids("hacks", startpage=1)
    assert len(ids) == 20
    assert calls == ["/?page=hacks&startpage=1"]


def test_list_ids_unknown_section():
    with pytest.raises(ValueError):
        hacks.list_ids("bogus")


def test_iter_ids_walks_multiple_pages(monkeypatch):
    """Three pages of 2 ids each, then an empty page stops the walk."""
    pages = {
        1: ["1", "2"],
        2: ["3", "4"],
        3: ["5", "6"],
        4: [],
    }

    def fake_list_ids(section, *, startpage=1):
        return pages.get(startpage, [])

    monkeypatch.setattr(hacks, "list_ids", fake_list_ids)
    ids = list(hacks.iter_ids("hacks"))
    assert ids == ["1", "2", "3", "4", "5", "6"]


def test_iter_ids_respects_max_pages(monkeypatch):
    pages = {1: ["1"], 2: ["2"], 3: ["3"]}
    monkeypatch.setattr(
        hacks, "list_ids", lambda section, *, startpage=1: pages.get(startpage, [])
    )
    ids = list(hacks.iter_ids("hacks", max_pages=2))
    assert ids == ["1", "2"]


def test_iter_ids_resumes_from_start_page(monkeypatch):
    pages = {5: ["50"], 6: ["60"], 7: []}
    monkeypatch.setattr(
        hacks, "list_ids", lambda section, *, startpage=1: pages.get(startpage, [])
    )
    ids = list(hacks.iter_ids("hacks", start=5))
    assert ids == ["50", "60"]


def test_iter_ids_stops_on_all_duplicate_page(monkeypatch):
    """A page whose ids were already seen ends the walk (loop guard)."""
    pages = {1: ["1", "2"], 2: ["1", "2"], 3: ["9"]}
    monkeypatch.setattr(
        hacks, "list_ids", lambda section, *, startpage=1: pages.get(startpage, [])
    )
    ids = list(hacks.iter_ids("hacks"))
    assert ids == ["1", "2"]


# ---- get_entry / iter_entries ---------------------------------------------


def test_get_entry_hack(monkeypatch, hack_html):
    monkeypatch.setattr(
        hacks.transport, "get_html", lambda path, params=None, **kw: hack_html
    )
    entry = hacks.get_entry("hacks", "1")
    assert isinstance(entry, Hack)
    assert entry.id == "1"


def test_get_entry_not_found_raises(monkeypatch):
    error_html = "<html><body><div class='topbar'><h2>Error Encountered!</h2></div></body></html>"
    monkeypatch.setattr(
        hacks.transport, "get_html", lambda path, params=None, **kw: error_html
    )
    with pytest.raises(NotFoundError):
        hacks.get_entry("hacks", "999999999")


def test_get_entry_unknown_section():
    with pytest.raises(ValueError):
        hacks.get_entry("bogus", "1")


def test_iter_entries_skips_404s(monkeypatch, hack_html):
    """iter_entries continues past a 404'd id instead of aborting the crawl."""
    error_html = "<html><body><div class='topbar'><h2>Error Encountered!</h2></div></body></html>"

    monkeypatch.setattr(hacks, "iter_ids", lambda section, **kw: iter(["1", "404", "2"]))

    def fake_get_html(path, params=None, **kw):
        if "/hacks/404/" in path:
            return error_html
        return hack_html

    monkeypatch.setattr(hacks.transport, "get_html", fake_get_html)
    entries = list(hacks.iter_entries("hacks"))
    assert len(entries) == 2
    assert all(isinstance(e, Hack) for e in entries)
