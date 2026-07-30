# Listing and fetch

`pyromhacking.hacks` enumerates section listings and fetches detail pages.
The four sections share one listing skeleton (`/?page=<section>&startpage=N`)
and one detail skeleton (`/<section>/<id>/`).

## Fetch one entry

```python
from pyromhacking import get_hack, get_translation, get_utility, get_document
from pyromhacking import get_entry

get_hack("1")                # Hack
get_translation("1")         # Translation
get_entry("utilities", "1")  # generic dispatch -> Utility
```

`get_entry` raises `NotFoundError` for ids that do not exist.

## Enumerate ids

```python
from pyromhacking import list_hacks, list_ids, iter_ids

list_hacks()                          # ids on the first listing page
list_ids("translations", startpage=2) # a specific page

for entry_id in iter_ids("hacks", max_pages=3):
    ...   # walks consecutive pages, dedupes, stops on an empty page
```

## Enumerate full entries

```python
from pyromhacking import iter_entries

for hack in iter_entries("hacks", max_pages=2):
    print(hack.title, hack.system)
```

`iter_entries` composes `iter_ids` and `get_entry`. It skips ids that 404
mid-walk instead of aborting the crawl.

## Politeness

Every fetch is throttled. See [transport.md](transport.md). For multi-page
crawls, raise the delay with `transport.set_delay(...)` and cap pages with
`max_pages`.

---
[← Models](models.md) · [Home](../README.md) · [Search →](search.md)
