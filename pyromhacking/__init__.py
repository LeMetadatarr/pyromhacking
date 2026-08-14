"""pyromhacking — Python HTML scraper for romhacking.net.

romhacking.net (RHDN) is the community database of ROM hacks, fan translations,
patching utilities and documentation. There is no official API; this library
fetches HTML pages and parses them with BeautifulSoup selectors. Field
extraction is best-effort against the current page structure and may need
adjustment if the site layout changes. It returns typed dataclasses for the
four catalogued sections and enumerates their listing pages.

The site sits behind Cloudflare; every request is routed through a FlareSolverr
instance (``PYROMHACKING_FLARESOLVERR_URL``). See :mod:`pyromhacking.transport`.

Quick start::

    import os
    os.environ["PYROMHACKING_FLARESOLVERR_URL"] = "http://localhost:8191"

    from pyromhacking import get_hack, list_hacks
    hack = get_hack("1")
    print(hack.title, hack.game, hack.system)
"""
import dataclasses
from typing import Dict, Iterator, List, Optional, Set

from pyromhacking._parse import NotFoundError
from pyromhacking.hacks import (
    SECTIONS,
    get_document,
    get_entry,
    get_hack,
    get_translation,
    get_utility,
    iter_entries,
    iter_ids,
    list_documents,
    list_hacks,
    list_ids,
    list_translations,
    list_utilities,
    search_documents,
    search_entries,
    search_hacks,
    search_translations,
    search_utilities,
)
from pyromhacking.ids import (
    document_to_extra,
    entry_to_extra,
    entry_url,
    hack_to_extra,
    parse_ref,
    translation_to_extra,
    utility_to_extra,
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
from pyromhacking.transport import reset_session, set_delay
from pyromhacking.version import __version__


def crawl(
    sections: Optional[List[str]] = None,
    *,
    seen: Optional[Set[str]] = None,
    max_entries: int = 0,
) -> Iterator[Dict]:
    if sections is None:
        sections = ["hacks", "translations"]
    if seen is None:
        seen = set()
    count = 0
    for section in sections:
        for entry in iter_entries(section):
            entry_id = getattr(entry, "id", None) or getattr(entry, "url", None)
            if entry_id is not None:
                if entry_id in seen:
                    continue
                seen.add(entry_id)
            try:
                if hasattr(entry, "as_dict"):
                    yield entry.as_dict
                elif dataclasses.is_dataclass(entry):
                    yield dataclasses.asdict(entry)
                else:
                    yield vars(entry)
            except Exception:
                continue
            count += 1
            if max_entries and count >= max_entries:
                return


__all__ = [
    # models
    "Credit",
    "Document",
    "DownloadFile",
    "Hack",
    "SECTION_MODELS",
    "SearchResult",
    "Translation",
    "Utility",
    # fetch / listing
    "SECTIONS",
    "get_document",
    "get_entry",
    "get_hack",
    "get_translation",
    "get_utility",
    "iter_entries",
    "iter_ids",
    "list_documents",
    "list_hacks",
    "list_ids",
    "list_translations",
    "list_utilities",
    "search_documents",
    "search_entries",
    "search_hacks",
    "search_translations",
    "search_utilities",
    # ids / cross-ref
    "document_to_extra",
    "entry_to_extra",
    "entry_url",
    "hack_to_extra",
    "parse_ref",
    "translation_to_extra",
    "utility_to_extra",
    # transport
    "reset_session",
    "set_delay",
    # errors / meta
    "NotFoundError",
    "__version__",
    # crawl
    "crawl",
]
