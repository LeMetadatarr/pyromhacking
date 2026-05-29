"""HF-publishable dataset builders for romhacking.net.

Four configs, one per catalogued section, each a stream of flat JSON rows:

- **hacks**        — ROM hacks (game, system, category, hack_type, version, ...)
- **translations** — fan translations (language, game, published_by, ...)
- **utilities**    — tools / patchers (os, language, ...)
- **documents**    — guides / docs (document_type, language, ...)

Rows are emitted lazily so a caller can :func:`export_jsonl` straight to disk
without holding a section in memory. Each row carries the canonical
``romhacking_id`` + ``section`` anchor plus the flattened ``extra`` cross-ref
keys from :mod:`pyromhacking.ids`.

Every row costs one FlareSolverr-routed fetch — treat a full export as a
homelab job and validate on a small ``--limit`` first. See ``docs/dataset.md``
and ``PROVENANCE.md``.

Run::

    python -m pyromhacking.dataset hacks --out hacks.jsonl --limit 10
    python -m pyromhacking.dataset all --out romhacking_dataset --limit 5
"""
from __future__ import annotations

import argparse
import json
from typing import Dict, Iterator, List, Optional

from pyromhacking import hacks as _hacks
from pyromhacking.ids import entry_to_extra

CONFIGS = ("hacks", "translations", "utilities", "documents")


def _row(entry) -> dict:
    """Flatten one entry into a dataset row."""
    d = dict(entry.as_dict)
    d["xref"] = entry_to_extra(entry)
    return d


def iter_rows(config: str, *, limit: Optional[int] = None,
              start: int = 1, max_pages: Optional[int] = None) -> Iterator[dict]:
    """Yield flat dataset rows for *config* (one of :data:`CONFIGS`).

    Args:
        config: which section to build.
        limit: cap on rows emitted (handy for validation).
        start: first listing page (1-based).
        max_pages: cap on listing pages walked.
    """
    if config not in CONFIGS:
        raise ValueError(f"unknown config {config!r}; expected one of {CONFIGS}")
    n = 0
    for entry in _hacks.iter_entries(config, start=start, max_pages=max_pages):
        if limit is not None and n >= limit:
            break
        yield _row(entry)
        n += 1


def export_jsonl(config: str, path: str, *, limit: Optional[int] = None,
                 start: int = 1, max_pages: Optional[int] = None,
                 verbose: bool = False) -> int:
    """Stream *config* rows to a JSONL file. Returns the row count written."""
    written = 0
    with open(path, "w", encoding="utf-8") as fh:
        for row in iter_rows(config, limit=limit, start=start, max_pages=max_pages):
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            written += 1
            if verbose and written % 25 == 0:
                print(f"  {config}: {written} rows")
    if verbose:
        print(f"wrote {written} {config} rows -> {path}")
    return written


def export_all(out_dir: str, *, limit: Optional[int] = None,
               max_pages: Optional[int] = None,
               verbose: bool = True) -> Dict[str, int]:
    """Export every config into ``{out_dir}/<config>.jsonl``. Returns counts."""
    import os

    os.makedirs(out_dir, exist_ok=True)
    counts: Dict[str, int] = {}
    for config in CONFIGS:
        path = os.path.join(out_dir, f"{config}.jsonl")
        counts[config] = export_jsonl(
            config, path, limit=limit, max_pages=max_pages, verbose=verbose
        )
    return counts


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build romhacking.net HF datasets (hacks / translations / "
                    "utilities / documents).")
    parser.add_argument("config", choices=(*CONFIGS, "all"),
                        help="dataset config to export")
    parser.add_argument("--out", help="output .jsonl file (or dir for 'all')")
    parser.add_argument("--limit", type=int, default=None,
                        help="cap on rows (validation)")
    parser.add_argument("--max-pages", type=int, default=None,
                        help="cap on listing pages walked")
    parser.add_argument("--delay", type=float, default=None,
                        help="seconds between HTTP requests (politeness)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if args.delay is not None:
        from pyromhacking import transport
        transport.set_delay(args.delay)

    verbose = not args.quiet
    if args.config == "all":
        out = args.out or "romhacking_dataset"
        counts = export_all(out, limit=args.limit, max_pages=args.max_pages,
                            verbose=verbose)
        if verbose:
            print("done:", counts)
        return 0

    out = args.out or f"{args.config}.jsonl"
    export_jsonl(args.config, out, limit=args.limit, max_pages=args.max_pages,
                 verbose=verbose)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
