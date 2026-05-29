# Cross-reference ids

`pyromhacking.ids` converts models into flat `ExternalIds.extra` dicts for the
metadatarr pipeline, and parses entry references back out of URLs.

## Anchor

The numeric id space is shared across sections (`/hacks/1/` and
`/translations/1/` are different entries), so the canonical anchor is the pair
**(`romhacking_section`, `romhacking_id`)**. A flat per-section key
(`romhacking_<section>_id`) is also written so a consumer can join on a single
field.

```python
from pyromhacking import get_hack, hack_to_extra

extra = hack_to_extra(get_hack("1"))
extra["romhacking_id"]        # "1"
extra["romhacking_section"]   # "hacks"
extra["romhacking_hacks_id"]  # "1"  (canonical anchor)
extra["romhacking_system"]    # "NES"
```

All keys are namespaced `romhacking_*`.

## Converters

| Function | Input |
| --- | --- |
| `hack_to_extra(hack)` | `Hack` |
| `translation_to_extra(tr)` | `Translation` |
| `utility_to_extra(util)` | `Utility` |
| `document_to_extra(doc)` | `Document` |
| `entry_to_extra(entry)` | any — dispatches on `entry.section` |

## URL helpers

```python
from pyromhacking import entry_url, parse_ref

entry_url("hacks", "1")                                  # canonical URL
parse_ref("https://www.romhacking.net/translations/7/")  # ("translations", "7")
```
