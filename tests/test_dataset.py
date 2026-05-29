"""Offline tests for the dataset builders (network stubbed via fixtures)."""
import json

import pytest

from pyromhacking import dataset
from pyromhacking._parse import parse_hack, parse_translation


@pytest.fixture
def stub_entries(monkeypatch, hack_html, translation_html):
    """Stub ``hacks.iter_entries`` to replay fixture-parsed entries."""
    pool = {
        "hacks": [parse_hack(hack_html, "1")],
        "translations": [parse_translation(translation_html, "1")],
        "utilities": [],
        "documents": [],
    }

    def fake_iter_entries(section, *, start=1, max_pages=None):
        for entry in pool.get(section, []):
            yield entry

    monkeypatch.setattr(dataset._hacks, "iter_entries", fake_iter_entries)
    return pool


def test_configs():
    assert dataset.CONFIGS == ("hacks", "translations", "utilities", "documents")


def test_iter_rows_hacks(stub_entries):
    rows = list(dataset.iter_rows("hacks"))
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == "1"
    assert row["section"] == "hacks"
    assert row["title"] == "Dragoon X Omega - Gold Edition"
    assert row["xref"]["romhacking_hacks_id"] == "1"


def test_iter_rows_limit(stub_entries):
    assert list(dataset.iter_rows("hacks", limit=0)) == []


def test_iter_rows_unknown_config():
    with pytest.raises(ValueError):
        list(dataset.iter_rows("nope"))


def test_export_jsonl(tmp_path, stub_entries):
    out = tmp_path / "hacks.jsonl"
    n = dataset.export_jsonl("hacks", str(out))
    assert n == 1
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["system"] == "NES"


def test_export_all(tmp_path, stub_entries):
    counts = dataset.export_all(str(tmp_path), verbose=False)
    assert counts == {"hacks": 1, "translations": 1, "utilities": 0, "documents": 0}
    assert (tmp_path / "translations.jsonl").exists()
