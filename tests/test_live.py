"""Live smoke test — hits romhacking.net through FlareSolverr.

Requires ``PYROMHACKING_FLARESOLVERR_URL`` to point at a reachable FlareSolverr
instance. Run with::

    pytest -m live

Deselected by default via ``-m 'not live'``.
"""
import os

import pytest

from pyromhacking import get_hack, get_utility, get_document, list_hacks, search_hacks, search_translations
from pyromhacking.models import Hack, SearchResult

pytestmark = pytest.mark.live

_HAS_SOLVER = bool(os.environ.get("PYROMHACKING_FLARESOLVERR_URL", "").strip())


@pytest.mark.skipif(not _HAS_SOLVER, reason="PYROMHACKING_FLARESOLVERR_URL not set")
def test_live_get_hack():
    hack = get_hack("1")
    assert isinstance(hack, Hack)
    assert hack.id == "1"
    assert hack.title
    assert hack.system
    assert hack.downloads is not None


@pytest.mark.skipif(not _HAS_SOLVER, reason="PYROMHACKING_FLARESOLVERR_URL not set")
def test_live_listing():
    ids = list_hacks()
    assert ids
    assert all(i.isdigit() for i in ids)


@pytest.mark.skipif(not _HAS_SOLVER, reason="PYROMHACKING_FLARESOLVERR_URL not set")
def test_live_search_hacks():
    page = search_hacks(title="zelda")
    assert page.total > 0
    assert len(page.results) > 0
    assert all(isinstance(r, SearchResult) for r in page.results)
    first = page.results[0]
    assert first.id
    assert first.title
    assert first.platform
    assert first.section == "hacks"


@pytest.mark.skipif(not _HAS_SOLVER, reason="PYROMHACKING_FLARESOLVERR_URL not set")
def test_live_search_translations():
    page = search_translations(title="zelda")
    assert page.total >= 0
    for r in page.results:
        assert r.section == "translations"
        assert r.id


@pytest.mark.skipif(not _HAS_SOLVER, reason="PYROMHACKING_FLARESOLVERR_URL not set")
def test_live_get_utility():
    from pyromhacking.models import Utility
    u = get_utility("1887")
    assert isinstance(u, Utility)
    assert u.title
    assert u.system


@pytest.mark.skipif(not _HAS_SOLVER, reason="PYROMHACKING_FLARESOLVERR_URL not set")
def test_live_get_document():
    from pyromhacking.models import Document
    doc = get_document("936")
    assert isinstance(doc, Document)
    assert doc.title
    assert doc.system
