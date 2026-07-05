# Changelog

## 2026-07-05 — Stage 0: repo bootstrap + scraper

### Decisions (grilled, see PLAN.md and docs/adr/)
- **ADR-0006 — fetch once, parse freely**: raw Page Snapshots (`data/html/`)
  are the permanent source of truth; Episode Records (`data/raw/`) are derived
  and freely re-parseable. Medallion architecture: bronze → silver → gold.
- **Manifest** widened to a per-episode status ledger
  (discovered → fetched → parsed / flagged → backfilled); flagged episodes are
  a filter, not a separate list.
- **Data contract**: required = episode, title, date, source URL, transcript
  text; speaker labels/summary/key points/links are optional enrichment
  recorded as gaps. Unlabeled transcripts stay in the Corpus.
- **Scraper is a permanent weekly tool** (Refresh), not a one-off; re-fetch
  only as deliberate correction. Manual `make refresh` during the core
  roadmap; Airflow-orchestrated automation queued as a stretch learning item.
- **All development in the devcontainer from day one**; nothing depends on
  host tooling.
- Politeness: sequential, 2 s delay, honest UA with contact email, backoff on
  5xx, hard halt on 403/429.

### Added
- Public repo <https://github.com/whokin/RRRAG> (code + docs only; data never
  committed, ADR-0001).
- `.devcontainer/` — Python 3.12 + uv image (uv via PyPI; ghcr.io pull timed
  out).
- `scraper/` package with CLI: `discover`, `fetch`, `parse`, `refresh`,
  `status`; `Makefile` targets `probe`, `refresh`, `status`, `sync-data`
  (stub).
- `docs/LEARNING.md` — learning journal, seeded with 9 entries.

### Probe findings (episodes 50/150/250/350/416 — all parse clean)
- Sitemap discovery found **511** `/podcast/` pages: 414 numeric episodes
  (1–416), 17-part crypto series, oddities (`90-2`, `388-x63ds`), 76
  topic/guest index pages (will flag at parse time).
- Four format eras handled: three title conventions; `[0:01:58.0]` vs
  `(0:04:01)` timestamps; `<strong>` vs plain speaker labels; #250's
  interview era (bold questions, unlabeled answers → 123/130 turns
  unattributed, recorded as a gap); links as anchors vs plain-text
  "Title — URL" with wrapped URLs; "Disclaimer:" boilerplate excluded from
  speakers.
- Episode-number inference restricted to pure-numeric slugs (`crypto1` is not
  episode 1).

### Full crawl results (bronze layer complete)
- All 511 discovered pages fetched (~20 min, zero blocks or retries).
- **412 canonical Episode Records** in `data/raw/`; **68 alias URLs** demoted
  (the "topic/guest pages" turned out to be alternate URLs for real episodes
  with byte-identical content — new Manifest state `alias`, canonical slug =
  pure-numeric first); **31 flagged** for backfill: 17 crypto-series episodes
  (no episode number — numbering decision pending), 4 numeric episodes with
  zero transcript text (98, 110, 114, 289), plus bonus/special pages.
- Speaker-label coverage (headline EDA number): 115 of 412 records have no
  speaker labels; the interview-era episodes have mostly unattributed turns.
  Full EDA in the corpus-stats notebook is next session's work.
- Data exists locally only — R2 bucket + `make sync-data` not yet set up.
