# Provenance

## Source

Data is scraped from [romhacking.net](https://www.romhacking.net) (RHDN), the
community database of ROM hacks, fan translations, patching utilities, and
documentation.

## Access

The site is served behind Cloudflare. This client reaches it only through a
[FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) instance
(`PYROMHACKING_FLARESOLVERR_URL`); requests are throttled by the transport to
stay polite.

## Authorship and rights

Entry content (titles, descriptions, credits, ratings, screenshots) is authored
and submitted by the romhacking.net community and its individual contributors.
This client extracts and reshapes that content; it does not assert ownership of
it. Downstream redistribution — including any Hugging Face dataset built with
`pyromhacking.dataset` — must respect the contributors' rights and the site's
terms.

## Scope

Captured fields per entry: title, game, system, category, hack type, language,
version, authors, release date, rating, download count, description, file links,
credits, and screenshot URLs. Patch files themselves are referenced by URL, not
downloaded.

## Fixtures

`tests/fixtures/` holds a small set of captured pages (one per section plus a
listing page) used for offline tests. They are snapshots for verification only.
