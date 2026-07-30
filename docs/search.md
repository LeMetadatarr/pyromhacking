# Search

romhacking.net exposes no JSON or AJAX API. All data, including search
results, is served as HTML pages. The search endpoint is the same URL used
for ordinary section listing pages, with extra GET parameters for filtering:

```
GET /?page=<section>&title=<query>[&author=<a>][&platform=<id>][&category=<id>][&startpage=<n>]
```

The response is a full HTML page containing a `<table>` with a caption of the
form `(X to Y) of Z Results`. Each row corresponds to one entry. The first
column title-links to the entry detail page (e.g. `/hacks/2796/`), from which
the numeric id is extracted.

## Using the search API

```python
import os
os.environ["PYROMHACKING_FLARESOLVERR_URL"] = "http://localhost:8191"

from pyromhacking import search_hacks, search_translations, search_utilities, search_documents

# Free-text title search in the hacks section
page = search_hacks(title="zelda")
print(f"{page.total} total results, {len(page.results)} on this page")

for r in page.results:
    print(r.id, r.title, r.platform, r.downloads)

# Translations, paginated
page2 = search_translations(title="dragon quest", startpage=1)

# Generic interface (any of the four sections)
from pyromhacking import search_entries
page3 = search_entries("utilities", title="tile")
```

## SearchResult fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Numeric entry id |
| `section` | str | `hacks` / `translations` / `utilities` / `documents` |
| `url` | str | Canonical entry URL |
| `title` | str | Entry title |
| `released_by` | str | Author / group |
| `game` | str | Original game title (hacks / translations) |
| `genre` | str | Genre string |
| `platform` | str | Console / system |
| `category` | str | Category label |
| `status` | str | e.g. `Fully Playable` (translations) |
| `language` | str | Language code (translations) |
| `downloads` | int | Download count |
| `date` | str | Release date string |

Call `get_entry(section, result.id)` to fetch the full detail record (`Hack`,
`Translation`, `Utility`, or `Document`).

## Pagination

Results are served 20 per page. Use `startpage` to walk pages:

```python
results = []
page = 1
while True:
    p = search_hacks(title="mario", startpage=page)
    results.extend(p.results)
    if p.page_to >= p.total:
        break
    page += 1
```

## No JSON endpoint

Active probing in May 2026 found no `api/`, `ajax/`, or JSON-returning
endpoint on romhacking.net. The site uses jQuery UI widgets, but all dynamic
content renders server-side and returns as HTML. Parsing uses BeautifulSoup
against the stable `<table>` result grid.

---
[← Listing & fetch](listing.md) · [Home](../README.md) · [Cross-reference ids →](ids.md)
