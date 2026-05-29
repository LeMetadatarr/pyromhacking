"""Live smoke test — hits romhacking.net through FlareSolverr.

Requires ``PYROMHACKING_FLARESOLVERR_URL`` to point at a reachable FlareSolverr
instance. Run with::

    pytest -m live

Deselected by default via ``-m 'not live'``.
"""
import os

import pytest

from pyromhacking import get_hack, list_hacks
from pyromhacking.models import Hack

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
