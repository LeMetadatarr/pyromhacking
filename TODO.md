# TODO

- **CI/CD.** No `.github/workflows/` is committed yet. Wire the repo up to the
  `gh-automations` reusable workflows (PR→`dev` alpha, release PR→`master`)
  rather than hand-rolling pipelines.
- **Search / filter.** Add a query interface over the listing
  (`/?page=hacks&...&genre=...&platform=...`) so callers can filter by system,
  category, or genre instead of walking every page.
- **Rating / hack-type coverage.** Some entries do not expose a rating or a
  hack-type row in `entryinfo`; confirm which page variants do and broaden the
  parser if a stable selector exists.
- **Games section.** RHDN `/games/<id>/` pages aggregate every entry for a
  title; a `games` entity could resolve a game once and link its hacks.
- **Fixture refresh.** Re-capture `tests/fixtures/*.html` if RHDN markup shifts.
