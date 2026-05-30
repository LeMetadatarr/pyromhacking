"""Listing enumeration and detail fetch for romhacking.net sections.

The four catalogued sections (``hacks``, ``translations``, ``utilities``,
``documents``) share one listing skeleton (``/?page=<section>&startpage=N``)
and one detail skeleton (``/<section>/<id>/``), so a single pair of functions
covers all of them, with thin per-section wrappers for ergonomics.

Every network call goes through :mod:`pyromhacking.transport`, which routes
through FlareSolverr — romhacking.net is Cloudflare-gated and unreachable
without it.
"""
from __future__ import annotations

from typing import Iterator, List, Optional

from pyromhacking import transport
from pyromhacking._parse import (
    NotFoundError,
    SearchResultPage,
    parse_entry,
    parse_listing,
    parse_search_results,
)
from pyromhacking.models import (
    Document,
    Hack,
    SECTION_MODELS,
    SearchResult,
    Translation,
    Utility,
)

SECTIONS = ("hacks", "translations", "utilities", "documents")

# Listing page size on romhacking.net (rows per startpage).
_PAGE_SIZE = 20


def _check_section(section: str) -> None:
    if section not in SECTIONS:
        raise ValueError(
            f"unknown section {section!r}; expected one of {SECTIONS}"
        )


def _listing_path(section: str, startpage: int) -> str:
    return f"/?page={section}&startpage={startpage}"


def list_ids(section: str, *, startpage: int = 1) -> List[str]:
    """Return the entry ids on one listing page of *section*.

    Args:
        section: one of :data:`SECTIONS`.
        startpage: 1-based listing page number.
    """
    _check_section(section)
    html = transport.get_html(_listing_path(section, startpage))
    return parse_listing(html, section)


def iter_ids(section: str, *, start: int = 1,
             max_pages: Optional[int] = None) -> Iterator[str]:
    """Yield entry ids across consecutive listing pages of *section*.

    Stops when a page yields no ids or after *max_pages* pages.

    Args:
        section: one of :data:`SECTIONS`.
        start: first listing page (1-based).
        max_pages: cap on pages walked; ``None`` walks until an empty page.
    """
    _check_section(section)
    page = start
    walked = 0
    seen: set = set()
    while max_pages is None or walked < max_pages:
        ids = list_ids(section, startpage=page)
        new = [i for i in ids if i not in seen]
        if not new:
            break
        for entry_id in new:
            seen.add(entry_id)
            yield entry_id
        walked += 1
        page += 1


def get_entry(section: str, entry_id: str):
    """Fetch and parse one entry from *section*.

    Returns the section-appropriate dataclass (:class:`~pyromhacking.models.Hack`,
    :class:`~pyromhacking.models.Translation`, ...).

    Raises:
        NotFoundError: if the id does not exist.
        ValueError: if *section* is unknown.
    """
    _check_section(section)
    html = transport.get_html(f"/{section}/{entry_id}/")
    return parse_entry(html, section, str(entry_id))


def iter_entries(section: str, *, start: int = 1,
                 max_pages: Optional[int] = None) -> Iterator:
    """Yield fully parsed entries across listing pages of *section*.

    Convenience composition of :func:`iter_ids` + :func:`get_entry`; skips ids
    that 404 mid-walk rather than aborting the crawl.
    """
    for entry_id in iter_ids(section, start=start, max_pages=max_pages):
        try:
            yield get_entry(section, entry_id)
        except NotFoundError:
            continue


# ---- search --------------------------------------------------------------


def search_entries(
    section: str,
    *,
    title: str = "",
    author: str = "",
    game: str = "",
    platform: int = 0,
    category: int = 0,
    startpage: int = 1,
) -> "SearchResultPage":
    """Search a section and return a :class:`~pyromhacking._parse.SearchResultPage`.

    Filters are sent as GET parameters to the romhacking.net listing page,
    which returns an HTML results table filtered server-side.

    Args:
        section: one of :data:`SECTIONS`.
        title: free-text filter applied to the entry title.
        author: free-text filter applied to the author / released-by field.
        game: free-text filter applied to the original game title.
        platform: numeric platform id (0 = any); see the site's dropdown.
        category: numeric category id (0 = any).
        startpage: 1-based results page.

    Returns:
        :class:`~pyromhacking._parse.SearchResultPage` with ``.results``,
        ``.total``, ``.page_from``, ``.page_to``.
    """
    _check_section(section)
    params: dict = {"page": section, "startpage": startpage}
    if title:
        params["title"] = title
    if author:
        params["author"] = author
    if game:
        params["game"] = game
    if platform:
        params["platform"] = platform
    if category:
        params["category"] = category
    html = transport.get_html("/", params=params)
    return parse_search_results(html, section)


def search_hacks(title: str = "", **kwargs) -> "SearchResultPage":
    """Search the hacks section.  See :func:`search_entries` for all params."""
    return search_entries("hacks", title=title, **kwargs)


def search_translations(title: str = "", **kwargs) -> "SearchResultPage":
    """Search the translations section."""
    return search_entries("translations", title=title, **kwargs)


def search_utilities(title: str = "", **kwargs) -> "SearchResultPage":
    """Search the utilities section."""
    return search_entries("utilities", title=title, **kwargs)


def search_documents(title: str = "", **kwargs) -> "SearchResultPage":
    """Search the documents section."""
    return search_entries("documents", title=title, **kwargs)


# ---- per-section convenience wrappers ------------------------------------


def get_hack(entry_id: str) -> Hack:
    """Fetch a ROM hack by id (``/hacks/<id>/``)."""
    return get_entry("hacks", entry_id)


def get_translation(entry_id: str) -> Translation:
    """Fetch a fan translation by id (``/translations/<id>/``)."""
    return get_entry("translations", entry_id)


def get_utility(entry_id: str) -> Utility:
    """Fetch a utility / tool by id (``/utilities/<id>/``)."""
    return get_entry("utilities", entry_id)


def get_document(entry_id: str) -> Document:
    """Fetch a document / guide by id (``/documents/<id>/``)."""
    return get_entry("documents", entry_id)


def list_hacks(*, startpage: int = 1) -> List[str]:
    """Entry ids on one listing page of ``/hacks/``."""
    return list_ids("hacks", startpage=startpage)


def list_translations(*, startpage: int = 1) -> List[str]:
    """Entry ids on one listing page of ``/translations/``."""
    return list_ids("translations", startpage=startpage)


def list_utilities(*, startpage: int = 1) -> List[str]:
    """Entry ids on one listing page of ``/utilities/``."""
    return list_ids("utilities", startpage=startpage)


def list_documents(*, startpage: int = 1) -> List[str]:
    """Entry ids on one listing page of ``/documents/``."""
    return list_ids("documents", startpage=startpage)
