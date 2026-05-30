"""Offline tests for search result parsing and all four section parsers."""
import pytest

from pyromhacking._parse import (
    NotFoundError,
    parse_document,
    parse_listing,
    parse_search_results,
    parse_utility,
)
from pyromhacking.models import Document, SearchResult, Utility


# ---- search result parsing -----------------------------------------------


def test_parse_search_hacks_count(search_hacks_html):
    page = parse_search_results(search_hacks_html, "hacks")
    assert page.total == 174
    assert page.page_from == 1
    assert page.page_to == 20
    assert len(page.results) == 20


def test_parse_search_hacks_fields(search_hacks_html):
    page = parse_search_results(search_hacks_html, "hacks")
    first = page.results[0]
    assert isinstance(first, SearchResult)
    assert first.id == "2796"
    assert first.section == "hacks"
    assert first.url == "https://www.romhacking.net/hacks/2796/"
    assert "Zelda" in first.title
    assert first.platform == "SNES"
    assert first.downloads is not None
    assert first.date


def test_parse_search_hacks_as_dict(search_hacks_html):
    page = parse_search_results(search_hacks_html, "hacks")
    d = page.results[0].as_dict
    assert d["id"] == "2796"
    assert d["section"] == "hacks"
    assert isinstance(d["downloads"], int)


def test_parse_search_translations_count(search_translations_html):
    page = parse_search_results(search_translations_html, "translations")
    assert page.total == 8
    assert len(page.results) == 8


def test_parse_search_translations_fields(search_translations_html):
    page = parse_search_results(search_translations_html, "translations")
    first = page.results[0]
    assert first.id == "2349"
    assert first.section == "translations"
    assert first.platform == "SNES"
    assert first.status == "Fully Playable"
    assert first.language in ("EN", "English", "en")


def test_search_result_str(search_hacks_html):
    page = parse_search_results(search_hacks_html, "hacks")
    s = str(page.results[0])
    assert "SNES" in s


def test_search_result_page_repr(search_hacks_html):
    page = parse_search_results(search_hacks_html, "hacks")
    r = repr(page)
    assert "174" in r
    assert "SearchResultPage" in r


def test_search_empty_page_returns_gracefully():
    html = "<html><body><p>No results</p></body></html>"
    page = parse_search_results(html, "hacks")
    assert page.results == []
    assert page.total == 0


# ---- listings for utilities and documents --------------------------------


def test_parse_utilities_listing(utilities_listing_html):
    ids = parse_listing(utilities_listing_html, "utilities")
    assert len(ids) >= 10
    assert all(i.isdigit() for i in ids)
    assert len(set(ids)) == len(ids)


def test_parse_documents_listing(documents_listing_html):
    ids = parse_listing(documents_listing_html, "documents")
    assert len(ids) >= 10
    assert all(i.isdigit() for i in ids)


# ---- utility detail page -------------------------------------------------


def test_parse_utility_core_fields(utility_html):
    u = parse_utility(utility_html, "1887")
    assert isinstance(u, Utility)
    assert u.id == "1887"
    assert u.section == "utilities"
    assert u.title
    assert u.system == "Nintendo 64"
    assert u.os == "OS Independent"
    assert u.downloads is not None
    assert u.url == "https://www.romhacking.net/utilities/1887/"


def test_parse_utility_as_dict(utility_html):
    u = parse_utility(utility_html, "1887")
    d = u.as_dict
    assert d["os"] == "OS Independent"
    assert d["section"] == "utilities"


# ---- document detail page ------------------------------------------------


def test_parse_document_core_fields(document_html):
    doc = parse_document(document_html, "936")
    assert isinstance(doc, Document)
    assert doc.id == "936"
    assert doc.section == "documents"
    assert doc.title
    assert doc.system == "Sega Genesis"
    assert doc.downloads is not None
    assert doc.url == "https://www.romhacking.net/documents/936/"


def test_parse_document_as_dict(document_html):
    doc = parse_document(document_html, "936")
    d = doc.as_dict
    assert d["section"] == "documents"
    assert "document_type" in d
    assert "language" in d
