"""Shared pytest fixtures: offline HTML loaded from ``tests/fixtures/``."""
import os

import pytest

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load(name: str) -> str:
    with open(os.path.join(FIXTURE_DIR, name), encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture
def hack_html() -> str:
    return load("hack_1.html")


@pytest.fixture
def translation_html() -> str:
    return load("translation_1.html")


@pytest.fixture
def listing_html() -> str:
    return load("hacks_listing.html")
