---
name: pyromhacking
description: Search romhacking.net hacks, fan translations, utilities, and documents on behalf of users who cannot navigate the website, providing voice-first accessible access to the ROM hacking community database.
---
# pyromhacking — romhacking.net for agents

## When to use

Use this skill whenever a user needs to find, browse, or learn about content on romhacking.net (RHDN) — ROM hacks, fan translations (games translated to other languages), patching utilities, or documentation/guides — and cannot or should not navigate the site directly. Primary audience: blind and low-vision users who rely on voice output to interact with a computer. The agent searches, fetches, and speaks results so the user never has to touch a browser.

## Install

```bash
pip install pyromhacking   # plus a FlareSolverr solver for live access (Cloudflare)
```

Set the solver URL before making any calls:

```python
import os
os.environ["PYROMHACKING_FLARESOLVERR_URL"] = "http://localhost:8191"
```

## Core operations

### `search_hacks(title, *, author, game, platform, startpage) -> SearchResultPage`

Search the hacks section by free-text filters. Returns a `SearchResultPage` with `.results` (list of `SearchResult`), `.total`, `.page_from`, `.page_to`.

```python
from pyromhacking import search_hacks

page = search_hacks(game="Zelda")
for r in page.results:
    print(r.title, r.platform, r.released_by, r.status)
```

Returned `SearchResult` fields: `id`, `section`, `url`, `title`, `released_by`, `game`, `genre`, `platform`, `category`, `status`, `language`, `downloads`, `date`.

---

### `search_translations(title, *, author, game, platform, startpage) -> SearchResultPage`

Search fan translations. Same signature and return type as `search_hacks`.

```python
from pyromhacking import search_translations

page = search_translations(game="Final Fantasy", author="")
for r in page.results:
    print(r.title, r.language, r.platform, r.status)
```

---

### `search_utilities(title, *, author, game, platform, startpage) -> SearchResultPage`

Search patching utilities and ROM tools.

```python
from pyromhacking import search_utilities

page = search_utilities(title="tile editor")
for r in page.results:
    print(r.title, r.released_by, r.platform)
```

---

### `search_documents(title, *, author, game, platform, startpage) -> SearchResultPage`

Search guides and documentation.

```python
from pyromhacking import search_documents

page = search_documents(game="Castlevania")
for r in page.results:
    print(r.title, r.released_by, r.date)
```

---

### `search_entries(section, *, title, author, game, platform, category, startpage) -> SearchResultPage`

Generic search across any of the four sections (`"hacks"`, `"translations"`, `"utilities"`, `"documents"`). All section-specific wrappers delegate here.

```python
from pyromhacking import search_entries

page = search_entries("hacks", title="", game="Metroid", platform=0)
```

---

### `get_hack(entry_id) -> Hack`

Fetch the full detail record for a ROM hack by its site id.

```python
from pyromhacking import get_hack

hack = get_hack("1")
print(hack.title, hack.game, hack.system, hack.version)
print(hack.description)
for f in hack.files:
    print(f.label, f.url)
```

`Hack` fields (beyond the common set): `hack_type`, `genre`, `patching_information`.  
Common fields: `id`, `section`, `url`, `title`, `game`, `system`, `category`, `version`, `authors`, `release_date`, `last_modified`, `status`, `rating`, `downloads`, `description`, `files` (list of `DownloadFile`), `credits` (list of `Credit`), `images`.

---

### `get_translation(entry_id) -> Translation`

Fetch a full fan translation record.

```python
from pyromhacking import get_translation

t = get_translation("42")
print(t.title, t.game, t.language, t.system, t.version, t.status)
```

Extra fields: `language`, `genre`, `published_by`, `game_date`, `game_description`, `patching_information`.

---

### `get_utility(entry_id) -> Utility`

Fetch a full utility/tool record.

```python
from pyromhacking import get_utility

u = get_utility("10")
print(u.title, u.os, u.language)
```

Extra fields: `os`, `language`.

---

### `get_document(entry_id) -> Document`

Fetch a full guide/document record.

```python
from pyromhacking import get_document

doc = get_document("5")
print(doc.title, doc.document_type, doc.language)
```

Extra fields: `document_type`, `language`.

---

### `iter_entries(section, *, start, max_pages) -> Iterator`

Walk consecutive listing pages, yielding fully parsed entry objects. Skips ids that 404 mid-walk. Use `max_pages` to cap crawl depth.

```python
from pyromhacking import iter_entries

for hack in iter_entries("hacks", max_pages=2):
    print(hack.title, hack.game, hack.system)
```

## Access notes

romhacking.net is behind Cloudflare and cannot be reached with a plain HTTP client. Live access requires a running [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) instance. Point the library at it with the environment variable:

```
PYROMHACKING_FLARESOLVERR_URL=http://localhost:8191
```

No other solver endpoints are supported. If the variable is unset, requests will fail at the transport layer.

## Speaking the results (accessibility)

- Summarize a hack or translation as: **title** — original game — author(s) — version and status (e.g. "Complete", "v1.2"). Example: "Super Metroid Redux — Super Metroid for SNES — by Jathys — version 2.0, complete."
- Offer the description on request ("Want me to read the description?"); it can be long, so prompt before reading it aloud.
- For "find translations for \<game\>", call `search_translations(game="<game>")` and read each result's title, language, and status in sequence.
- For download links, read the label and full URL so the user can copy or hand off to a download manager — do not assume they can click.
