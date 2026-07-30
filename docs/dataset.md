# Dataset

`pyromhacking.dataset` builds HF-publishable JSONL datasets from
romhacking.net. It has four configs, one per catalogued section:

| Config | Section | Notable fields |
| --- | --- | --- |
| `hacks` | ROM hacks | game, system, category, hack_type, genre, version |
| `translations` | fan translations | language, game, published_by, status |
| `utilities` | tools / patchers | os, language |
| `documents` | guides / docs | document_type, language |

Each row is the model's `.as_dict` plus an `xref` block: the flattened
`romhacking_*` cross-reference keys from [ids](ids.md), anchored on
`romhacking_section` and `romhacking_id`.

## CLI

```bash
export PYROMHACKING_FLARESOLVERR_URL=http://localhost:8191

# validate on a small sample first
python -m pyromhacking.dataset hacks --out hacks.jsonl --limit 10 --delay 2

# walk a bounded number of listing pages
python -m pyromhacking.dataset translations --out tr.jsonl --max-pages 5

# every config into a directory
python -m pyromhacking.dataset all --out romhacking_dataset --limit 5
```

The console entry point `pyromhacking-dataset` does the same thing.

## Programmatic

```python
from pyromhacking import dataset

for row in dataset.iter_rows("hacks", limit=10):
    ...

dataset.export_jsonl("hacks", "hacks.jsonl", limit=100)
dataset.export_all("out_dir")
```

## Cost and politeness

Every row costs one FlareSolverr-routed fetch for the listing and the detail
page. A full export of all four sections needs tens of thousands of
requests. Run it on a dedicated machine, raise the delay (`--delay`), and
validate locally with `--limit` first.

## Provenance

The romhacking.net community authors the content. See
[../PROVENANCE.md](../PROVENANCE.md) before you redistribute it.

---
[← Cross-reference ids](ids.md) · [Home](../README.md)
