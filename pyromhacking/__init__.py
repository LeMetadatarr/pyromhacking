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
    Translation,
    Utility,
)
from pyromhacking.transport import reset_session, set_delay
from pyromhacking.version import __version__

__all__ = [
    # models
    "Credit",
    "Document",
    "DownloadFile",
    "Hack",
    "SECTION_MODELS",
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
]
