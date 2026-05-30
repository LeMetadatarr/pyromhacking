"""Typed data models for romhacking.net entries.

The site has four catalogued sections, each rendered with the same page
skeleton (an ``entryinfo`` table plus a description block):

* :class:`Hack`        — ROM hacks (``/hacks/<id>/``)
* :class:`Translation` — fan translations (``/translations/<id>/``)
* :class:`Utility`     — tools / patchers (``/utilities/<id>/``)
* :class:`Document`    — guides / docs (``/documents/<id>/``)

All four share a common field set; section-specific fields (language for
translations, OS for utilities, ...) are present on the relevant dataclass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Credit:
    """A single contributor row from an entry's Credits table."""

    contributor: str = ""
    contribution: str = ""
    listed_credit: str = ""

    @property
    def as_dict(self) -> dict:
        return {
            "contributor": self.contributor,
            "contribution": self.contribution,
            "listed_credit": self.listed_credit,
        }


@dataclass
class DownloadFile:
    """A downloadable patch / file link on an entry page."""

    label: str = ""
    url: str = ""

    @property
    def as_dict(self) -> dict:
        return {"label": self.label, "url": self.url}


@dataclass
class _Entry:
    """Common fields shared by every romhacking.net section entry."""

    id: str = ""
    section: str = ""
    url: str = ""
    title: str = ""
    game: str = ""
    game_url: str = ""
    system: str = ""  # console / platform
    category: str = ""
    version: str = ""
    authors: List[str] = field(default_factory=list)
    release_date: str = ""
    last_modified: str = ""
    status: str = ""
    rating: Optional[float] = None
    downloads: Optional[int] = None
    description: str = ""
    files: List[DownloadFile] = field(default_factory=list)
    credits: List[Credit] = field(default_factory=list)
    images: List[str] = field(default_factory=list)

    @property
    def console(self) -> str:
        """Alias for :attr:`system` (platform / console name)."""
        return self.system

    def _base_dict(self) -> dict:
        return {
            "id": self.id,
            "section": self.section,
            "url": self.url,
            "title": self.title,
            "game": self.game,
            "game_url": self.game_url,
            "system": self.system,
            "category": self.category,
            "version": self.version,
            "authors": self.authors,
            "release_date": self.release_date,
            "last_modified": self.last_modified,
            "status": self.status,
            "rating": self.rating,
            "downloads": self.downloads,
            "description": self.description,
            "files": [f.as_dict for f in self.files],
            "credits": [c.as_dict for c in self.credits],
            "images": self.images,
        }

    @property
    def as_dict(self) -> dict:
        return self._base_dict()

    def __str__(self) -> str:
        return f"{self.title} ({self.system})" if self.system else self.title


@dataclass
class Hack(_Entry):
    """A ROM hack entry (``/hacks/<id>/``)."""

    section: str = "hacks"
    hack_type: str = ""
    genre: str = ""
    patching_information: str = ""

    @property
    def as_dict(self) -> dict:
        d = self._base_dict()
        d.update(
            hack_type=self.hack_type,
            genre=self.genre,
            patching_information=self.patching_information,
        )
        return d


@dataclass
class Translation(_Entry):
    """A fan-translation entry (``/translations/<id>/``)."""

    section: str = "translations"
    language: str = ""
    genre: str = ""
    published_by: str = ""
    game_date: str = ""
    game_description: str = ""
    patching_information: str = ""

    @property
    def as_dict(self) -> dict:
        d = self._base_dict()
        d.update(
            language=self.language,
            genre=self.genre,
            published_by=self.published_by,
            game_date=self.game_date,
            game_description=self.game_description,
            patching_information=self.patching_information,
        )
        return d


@dataclass
class Utility(_Entry):
    """A utility / tool entry (``/utilities/<id>/``)."""

    section: str = "utilities"
    os: str = ""
    language: str = ""

    @property
    def as_dict(self) -> dict:
        d = self._base_dict()
        d.update(os=self.os, language=self.language)
        return d


@dataclass
class Document(_Entry):
    """A document / guide entry (``/documents/<id>/``)."""

    section: str = "documents"
    document_type: str = ""
    language: str = ""

    @property
    def as_dict(self) -> dict:
        d = self._base_dict()
        d.update(document_type=self.document_type, language=self.language)
        return d


@dataclass
class SearchResult:
    """A single row returned by a romhacking.net search / listing page.

    These are lightweight summary records parsed from the results table.
    Call :func:`~pyromhacking.hacks.get_entry` with ``id`` and ``section``
    to fetch the full :class:`_Entry` detail.
    """

    id: str = ""
    section: str = ""
    url: str = ""
    title: str = ""
    released_by: str = ""
    game: str = ""
    genre: str = ""
    platform: str = ""
    category: str = ""
    status: str = ""
    language: str = ""
    downloads: Optional[int] = None
    date: str = ""

    @property
    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "section": self.section,
            "url": self.url,
            "title": self.title,
            "released_by": self.released_by,
            "game": self.game,
            "genre": self.genre,
            "platform": self.platform,
            "category": self.category,
            "status": self.status,
            "language": self.language,
            "downloads": self.downloads,
            "date": self.date,
        }

    def __str__(self) -> str:
        return f"{self.title} ({self.platform})" if self.platform else self.title


# Section name -> model class, for generic dispatch.
SECTION_MODELS = {
    "hacks": Hack,
    "translations": Translation,
    "utilities": Utility,
    "documents": Document,
}
