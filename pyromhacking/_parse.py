"""HTML parsing for romhacking.net entry and listing pages.

Every section page shares the same skeleton::

    <div class="newsitem">
      <div class="topbar">
        <h2>TITLE</h2>
        <div class="date">GAME / SUBTITLE</div>
      </div>
      <div class="transbody">
        <table class="entryinfo ...">      # <th>label</th><td>value</td> rows
        <div class="entrybody...">         # <h3>Description:</h3> blocks
      </div>
    </div>

so a single field extractor drives all four section parsers.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

from pyromhacking._clean import (
    clean,
    clean_multiline,
    clean_or_none,
    id_from_url,
    parse_float,
    parse_int,
)
from pyromhacking.models import (
    Credit,
    Document,
    DownloadFile,
    Hack,
    SECTION_MODELS,
    SearchResult,
    Translation,
    Utility,
)


class NotFoundError(Exception):
    """Raised when an entry id does not exist (RHDN 'Error Encountered!')."""


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def is_error_page(soup: BeautifulSoup) -> bool:
    """True if the page is the RHDN 'does not exist' error placeholder."""
    if _entry_table(soup) is not None:
        return False
    for bar in soup.find_all(class_="topbar"):
        if "error encountered" in bar.get_text(strip=True).lower():
            return True
    text = soup.get_text(" ").lower()
    return "error encountered" in text or "does not exist" in text


def _entry_table(soup: BeautifulSoup):
    """The ``entryinfo`` table for the *content* entry (skips nav widgets)."""
    return soup.find("table", class_="entryinfo")


def _entry_item(soup: BeautifulSoup):
    """The ``newsitem`` block that actually holds the entry.

    The page chrome (sidebar Sections / Community / ... menus) reuses the same
    ``newsitem``/``topbar`` skeleton, so the content block is identified as the
    one wrapping the ``entryinfo`` table rather than the first one on the page.
    """
    table = _entry_table(soup)
    if table is not None:
        item = table.find_parent(class_="newsitem")
        if item is not None:
            return item
    return soup.find(class_="newsitem")


def _info_rows(soup: BeautifulSoup) -> Dict[str, Tuple[str, Optional[str]]]:
    """Map each ``entryinfo`` table label to (text, first-link-href)."""
    rows: Dict[str, Tuple[str, Optional[str]]] = {}
    table = _entry_table(soup)
    if not table:
        return rows
    for tr in table.find_all("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if not th or not td:
            continue
        label = clean(th.get_text()).rstrip(":").lower()
        link = td.find("a", href=True)
        href = link["href"] if link else None
        rows[label] = (clean(td.get_text()), href)
    return rows


def _row(rows: Dict[str, Tuple[str, Optional[str]]], *labels: str) -> str:
    for label in labels:
        if label in rows:
            return rows[label][0]
    return ""


def _row_href(rows: Dict[str, Tuple[str, Optional[str]]], *labels: str) -> Optional[str]:
    for label in labels:
        if label in rows and rows[label][1]:
            return rows[label][1]
    return None


def _authors(rows: Dict[str, Tuple[str, Optional[str]]], *labels: str) -> List[str]:
    raw = _row(rows, *labels)
    if not raw:
        return []
    parts = re.split(r"\s*(?:,|&|/| and )\s*", raw)
    return [p for p in (clean(p) for p in parts) if p]


def _description_blocks(soup: BeautifulSoup) -> Dict[str, str]:
    """Map each ``<h3>HEADING:</h3>`` in the body to its following text block."""
    blocks: Dict[str, str] = {}
    item = _entry_item(soup) or soup
    body = item.find(class_=re.compile(r"\bentrybody")) or item
    for h3 in body.find_all("h3"):
        heading = clean(h3.get_text()).rstrip(":").lower()
        sib = h3.find_next_sibling("div")
        if sib is not None:
            blocks[heading] = clean_multiline(sib.get_text("\n"))
    return blocks


def _files(soup: BeautifulSoup) -> List[DownloadFile]:
    files: List[DownloadFile] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/download/" in href:
            files.append(DownloadFile(label=clean(a.get_text()) or "Download", url=href))
    return files


def _images(soup: BeautifulSoup) -> List[str]:
    imgs: List[str] = []
    for gal in soup.find_all(class_="imageGallery"):
        for a in gal.find_all("a", href=True):
            if a["href"] not in imgs:
                imgs.append(a["href"])
    return imgs


def _credits(soup: BeautifulSoup) -> List[Credit]:
    creds: List[Credit] = []
    for cap in soup.find_all("caption"):
        if clean(cap.get_text()).lower() != "credits":
            continue
        table = cap.find_parent("table")
        if not table:
            continue
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) >= 2:
                creds.append(
                    Credit(
                        contributor=clean(cells[0].get_text()),
                        contribution=clean(cells[1].get_text()),
                        listed_credit=clean(cells[2].get_text()) if len(cells) > 2 else "",
                    )
                )
    return creds


def _rating(soup: BeautifulSoup) -> Optional[float]:
    text = soup.get_text(" ")
    m = re.search(r"Rating[^0-9]{0,12}(\d+(?:\.\d+)?)\s*/\s*10", text, re.I)
    if m:
        return parse_float(m.group(1))
    return None


def _title_and_subtitle(soup: BeautifulSoup) -> Tuple[str, str]:
    item = _entry_item(soup)
    title = ""
    subtitle = ""
    if item:
        topbar = item.find(class_="topbar")
        if topbar:
            h2 = topbar.find(["h2", "h1"])
            if h2:
                title = clean(h2.get_text())
            date = topbar.find(class_="date")
            if date:
                subtitle = clean(date.get_text())
    return title, subtitle


_GAME_PREFIX = re.compile(r"^(?:hack|translation|utility|document)\s+(?:of|for)\s+", re.I)


def _game(soup: BeautifulSoup) -> Tuple[str, str]:
    """Return (game_name, game_url) for the entry.

    The game is linked from the ``date`` subtitle (``Hack of <game>``); the
    entryinfo table on current pages no longer carries a ``/games/`` link.
    """
    item = _entry_item(soup)
    if item:
        topbar = item.find(class_="topbar")
        if topbar:
            date = topbar.find(class_="date")
            if date:
                link = date.find("a", href=True)
                if link and "/games/" in link["href"]:
                    return clean(link.get_text()), link["href"]
                raw = clean(date.get_text())
                if _GAME_PREFIX.search(raw):
                    txt = _GAME_PREFIX.sub("", raw)
                    if txt:
                        return txt, ""
    table = _entry_table(soup)
    if table:
        for a in table.find_all("a", href=True):
            if "/games/" in a["href"]:
                return clean(a.get_text()), a["href"]
    return "", ""


def _common(soup: BeautifulSoup, section: str, entry_id: str) -> dict:
    rows = _info_rows(soup)
    title, subtitle = _title_and_subtitle(soup)
    game, game_url = _game(soup)
    if not game:
        game = subtitle
    blocks = _description_blocks(soup)
    if not game and section in ("translations", "documents", "utilities"):
        # the date subtitle holds the platform, not a "Hack of <game>" link
        game = title
        game_url = ""
    description = (
        blocks.get("description")
        or blocks.get("translation description")
        or blocks.get("document description")
        or ""
    )
    return {
        "id": entry_id,
        "url": f"https://www.romhacking.net/{section}/{entry_id}/",
        "title": title,
        "game": game,
        "game_url": game_url,
        "system": _row(rows, "platform", "console", "system"),
        "category": _row(rows, "category"),
        "version": _row(rows, "patch version", "version"),
        "authors": _authors(rows, "released by", "author", "released by:"),
        "release_date": _row(rows, "release date"),
        "last_modified": _row(rows, "last modified"),
        "status": _row(rows, "status"),
        "rating": _rating(soup),
        "downloads": parse_int(_row(rows, "downloads")),
        "description": description,
        "files": _files(soup),
        "credits": _credits(soup),
        "images": _images(soup),
    }, rows, blocks


def parse_hack(html: str, entry_id: str) -> Hack:
    soup = _soup(html)
    if is_error_page(soup):
        raise NotFoundError(f"hacks/{entry_id} does not exist")
    base, rows, _ = _common(soup, "hacks", entry_id)
    return Hack(
        **base,
        hack_type=_row(rows, "hack type"),
        genre=_row(rows, "genre"),
        patching_information=_row(rows, "patching information"),
    )


def parse_translation(html: str, entry_id: str) -> Translation:
    soup = _soup(html)
    if is_error_page(soup):
        raise NotFoundError(f"translations/{entry_id} does not exist")
    base, rows, blocks = _common(soup, "translations", entry_id)
    return Translation(
        **base,
        language=_row(rows, "language"),
        genre=_row(rows, "genre"),
        published_by=_row(rows, "published by"),
        game_date=_row(rows, "game date"),
        game_description=blocks.get("game description", ""),
        patching_information=_row(rows, "patching information"),
    )


def parse_utility(html: str, entry_id: str) -> Utility:
    soup = _soup(html)
    if is_error_page(soup):
        raise NotFoundError(f"utilities/{entry_id} does not exist")
    base, rows, _ = _common(soup, "utilities", entry_id)
    if not base["authors"]:
        base["authors"] = _authors(rows, "author")
    return Utility(
        **base,
        os=_row(rows, "os", "operating system"),
        language=_row(rows, "language"),
    )


def parse_document(html: str, entry_id: str) -> Document:
    soup = _soup(html)
    if is_error_page(soup):
        raise NotFoundError(f"documents/{entry_id} does not exist")
    base, rows, _ = _common(soup, "documents", entry_id)
    if not base["authors"]:
        base["authors"] = _authors(rows, "author")
    return Document(
        **base,
        document_type=_row(rows, "document type", "type"),
        language=_row(rows, "language"),
    )


_PARSERS = {
    "hacks": parse_hack,
    "translations": parse_translation,
    "utilities": parse_utility,
    "documents": parse_document,
}


def parse_entry(html: str, section: str, entry_id: str):
    """Dispatch to the parser for ``section``."""
    if section not in _PARSERS:
        raise ValueError(f"unknown section: {section!r}")
    return _PARSERS[section](html, entry_id)


def parse_listing(html: str, section: str) -> List[str]:
    """Extract entry ids linked from a section listing page."""
    soup = _soup(html)
    ids: List[str] = []
    seen = set()
    pat = re.compile(rf"/{section}/(\d+)/?$")
    for a in soup.find_all("a", href=True):
        m = pat.search(a["href"])
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            ids.append(m.group(1))
    return ids


def parse_search_results(html: str, section: str) -> "SearchResultPage":
    """Parse a search/listing results table into a :class:`SearchResultPage`.

    The results table has a caption ``(X to Y) of Z Results`` and column
    headers that vary by section.  This function maps whatever columns are
    present to :class:`~pyromhacking.models.SearchResult` fields.

    Returns:
        :class:`SearchResultPage` with ``.results``, ``.total``,
        ``.page_from``, ``.page_to``.
    """
    soup = _soup(html)
    table = soup.find("table")
    results: List[SearchResult] = []
    total = page_from = page_to = 0

    if not table:
        return SearchResultPage(results=results, total=total,
                                page_from=page_from, page_to=page_to)

    cap = table.find("caption")
    if cap:
        m = re.search(r"\((\d+)\s+to\s+(\d+)\)\s+of\s+(\d+)", cap.get_text())
        if m:
            page_from, page_to, total = int(m.group(1)), int(m.group(2)), int(m.group(3))

    rows = table.find_all("tr")
    if not rows:
        return SearchResultPage(results=results, total=total,
                                page_from=page_from, page_to=page_to)

    # Parse column headers from first row
    header_row = rows[0]
    headers = [clean(th.get_text()).lower()
               for th in header_row.find_all(["th", "td"])]

    col = {h: i for i, h in enumerate(headers)}

    def _cell(cells, key: str, *fallbacks: str) -> str:
        for k in (key, *fallbacks):
            idx = col.get(k)
            if idx is not None and idx < len(cells):
                return clean(cells[idx].get_text())
        return ""

    pat = re.compile(rf"/{re.escape(section)}/(\d+)/?")
    base_url = f"https://www.romhacking.net/{section}/"

    for row in rows[1:]:
        cells = row.find_all("td")
        if not cells:
            continue
        # Find the section-specific link to get the entry id
        entry_id = ""
        title_link_url = ""
        for a in row.find_all("a", href=True):
            m = pat.search(a["href"])
            if m:
                entry_id = m.group(1)
                title_link_url = base_url + entry_id + "/"
                break
        if not entry_id:
            continue

        results.append(SearchResult(
            id=entry_id,
            section=section,
            url=title_link_url,
            title=_cell(cells, "title"),
            released_by=_cell(cells, "released by"),
            game=_cell(cells, "original game", "game"),
            genre=_cell(cells, "genre"),
            platform=_cell(cells, "platform"),
            category=_cell(cells, "category"),
            status=_cell(cells, "status"),
            language=_cell(cells, "lang", "language"),
            downloads=parse_int(_cell(cells, "downloads")),
            date=_cell(cells, "date"),
        ))

    return SearchResultPage(results=results, total=total,
                            page_from=page_from, page_to=page_to)


class SearchResultPage:
    """Return value from :func:`parse_search_results`."""

    __slots__ = ("results", "total", "page_from", "page_to")

    def __init__(
        self,
        results: List[SearchResult],
        total: int,
        page_from: int,
        page_to: int,
    ) -> None:
        self.results = results
        self.total = total
        self.page_from = page_from
        self.page_to = page_to

    def __len__(self) -> int:
        return len(self.results)

    def __iter__(self):
        return iter(self.results)

    def __repr__(self) -> str:
        return (
            f"SearchResultPage(total={self.total}, "
            f"page={self.page_from}-{self.page_to}, "
            f"results={len(self.results)})"
        )


def parse_listing_next_page(html: str) -> Optional[int]:
    """Return the highest ``startpage=N`` linked from a listing, if any."""
    soup = _soup(html)
    pages: List[int] = []
    for a in soup.find_all("a", href=True):
        m = re.search(r"startpage=(\d+)", a["href"])
        if m:
            pages.append(int(m.group(1)))
    return max(pages) if pages else None
