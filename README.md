# pyromhacking

`pyromhacking` is a Python HTML scraper for [romhacking.net](https://www.romhacking.net)
(RHDN), the community database of ROM hacks, fan translations, patching
utilities, and documentation. The site has no official API, so the library
fetches HTML pages and parses them with BeautifulSoup selectors. Field
extraction is best-effort against the current page structure and may need
adjustment if the site layout changes. It returns typed dataclasses for the
four catalogued sections, enumerates listing pages, and exports
Hugging-Face-publishable datasets.

## FlareSolverr required

romhacking.net sits behind Cloudflare. The client routes every request through
a [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) instance.
Without one, requests resolve to a challenge page instead of data.

```bash
export PYROMHACKING_FLARESOLVERR_URL=http://localhost:8191
```

## Install

```bash
pip install -e .
```

## Usage

```python
from pyromhacking import get_hack, list_hacks, iter_entries

hack = get_hack("1")
print(hack.title, hack.game, hack.system, hack.downloads)

for entry_id in list_hacks():
    print(entry_id)

for h in iter_entries("hacks", max_pages=2):
    print(h)
```

### Sections

The library covers four sections: `hacks`, `translations`, `utilities`,
`documents`. Fetch an entry with `get_hack` / `get_translation` /
`get_utility` / `get_document`, or the generic `get_entry(section, id)`.

### Dataset export

```bash
python -m pyromhacking.dataset all --out romhacking_dataset --limit 5
```

## Documentation

- [Quickstart](docs/quickstart.md)
- [Transport / FlareSolverr](docs/transport.md)
- [Models](docs/models.md)
- [Listing & fetch](docs/listing.md)
- [Search](docs/search.md)
- [Cross-reference ids](docs/ids.md)
- [Dataset](docs/dataset.md)

See [`examples/`](examples) for runnable scripts and [PROVENANCE.md](PROVENANCE.md)
for data provenance.

## Related projects

- [LeMetadatarr/pyrateyourmusic](https://github.com/LeMetadatarr/pyrateyourmusic)
- [LeMetadatarr/pysmwcentral](https://github.com/LeMetadatarr/pysmwcentral)
- [LeMetadatarr/pytcrf](https://github.com/LeMetadatarr/pytcrf)
- [LeMetadatarr/pytvtropes](https://github.com/LeMetadatarr/pytvtropes)

## Tests

```bash
pytest -m "not live"     # offline, fixture-based
PYROMHACKING_FLARESOLVERR_URL=... pytest -m live   # live smoke
```

## License

Apache-2.0. Scraped content is © the romhacking.net community.
