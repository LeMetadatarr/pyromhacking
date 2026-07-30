# Models

Each catalogued section maps to a dataclass in `pyromhacking.models`. All four
share a common field set (`_Entry`). Section-specific fields are added per
type.

## Common fields (`_Entry`)

| Field | Type | Notes |
| --- | --- | --- |
| `id` | str | numeric entry id |
| `section` | str | `hacks` / `translations` / `utilities` / `documents` |
| `url` | str | canonical entry URL |
| `title` | str | entry title |
| `game` | str | the game the entry targets |
| `game_url` | str | game page URL when linked |
| `system` | str | console / platform (alias: `.console`) |
| `category` | str | |
| `version` | str | patch version |
| `authors` | list[str] | |
| `release_date` | str | |
| `last_modified` | str | |
| `status` | str | |
| `rating` | float \| None | when the page exposes a score |
| `downloads` | int \| None | |
| `description` | str | multi-paragraph body |
| `files` | list[DownloadFile] | patch / file links |
| `credits` | list[Credit] | contributor rows |
| `images` | list[str] | screenshot URLs |

## Section types

- `Hack` adds `hack_type`, `genre`, `patching_information`.
- `Translation` adds `language`, `genre`, `published_by`, `game_date`,
  `game_description`, `patching_information`.
- `Utility` adds `os`, `language`.
- `Document` adds `document_type`, `language`.

## Serialization

Every model has `.as_dict`, which recursively flattens the nested `files` and
`credits` lists, and a `__str__` method (`"<title> (<system>)"`).

```python
from pyromhacking import get_hack
hack = get_hack("1")
hack.as_dict["downloads"]   # 6523
str(hack)                   # "Dragoon X Omega - Gold Edition (NES)"
```

`SECTION_MODELS` maps a section name to its class for generic dispatch.

---
[← Transport / FlareSolverr](transport.md) · [Home](../README.md) · [Listing & fetch →](listing.md)
