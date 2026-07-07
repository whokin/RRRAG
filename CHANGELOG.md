# Changelog

## 2026-07-06 — attribution enrichment + speaker table + notebook second pass

### Decisions
- **Attribute only where evidence is strong (validated on all 143 interview
  episodes):** answer-style turns get `inferred_speaker` = the title's guest
  (142/143 extractable, 0 multi-guest, first-name addressing corroborates
  113/142, Q→A alternation 98% clean). Question turns stay unattributed —
  101/143 interview episodes have zero in-episode evidence of which hosts
  were present, and we don't assert what the page doesn't support. Chunks
  will carry `turn_style` so questions remain filterable without name claims.
- Generation-side rule (for Stage 1+): `speaker_source = "inferred"` chunks
  are attributed as "the hosts asked / the guest said", never as a named
  host's personal view — multi-tagging hosts would conflate "one of them
  asked this" (true) with "they co-endorse this" (often false).
- Entity resolution via curated table (`scraper/speakers.py`), not NER: 298
  labels → canonical map (Benjamin/Ben Felix + 776 turns merged) + junk set
  (book titles, section markers). Observed `speaker` fields never rewritten.

### Added / fixed
- `scraper enrich` CLI step (silver-layer enrichment, re-runnable; part of
  `refresh`); junk labels excluded at parse; `Disclosure` boilerplate;
  speaker regex tolerates space before colon (recovered ~580 labeled turns).
- Notebook second pass: speaker inventory, attribution coverage, boilerplate
  scan.

### Coverage after enrichment
- **95.6% of transcript text attributed** (71.1% observed + 24.5% inferred
  guest), vs 71.3% before. Unattributed questions: 3.6%; boilerplate 0.5%.
- Boilerplate: 294/430 transcripts share one intro line; 202/430 have
  disclaimer-ish tails — tag at chunk time, keep in records.

## 2026-07-05 (later) — corpus-stats EDA + crypto series joins the Corpus

### Decisions (grilled)
- **Episode identity is (series, number)** — Option B over string
  pseudo-numbers: `series: "main" | "crypto"`, number stays an integer,
  extracted from titles ("Understanding Crypto 5"), no hardcoded lists.
  "C5"-style short forms are display conventions only. Glossary updated.
- Raw filenames stay **slug-based** (provenance over browsability; identity
  lives in the Manifest, filenames-as-metadata go stale).
- EDA notebook lives in `experiments/` (first citizen of the ADR-0002
  sandbox), committed output-free; pandas/matplotlib/jupyter are dev-group
  deps; token numbers are chars/4 estimates until Stage 1 counts for real.

### Corpus after this session
- **430 Episode Records** (413 main + 17 crypto), 68 aliases, **13 flagged**.
- Parser fallback recovers *unmarked* transcripts (≥20 speaker-labeled
  paragraphs, no section headers) — recovered #289.

### EDA findings (experiments/corpus_stats.ipynb)
- Coverage: links 99.8%, key points 99.1%, summary 96.3%, **speaker labels
  76.5%** — no-label episodes are 90 main-series (all in #11–#214, the early
  era) + 11 crypto; 28.7% of transcript *text* is unattributed.
- Size: **~6.6M transcript tokens** (PLAN guessed 15–20M — 2.5–3× over), →
  **~9.8k chunks** at 800 tokens/15% overlap (PLAN guessed 50–65k). Embedding
  cost is well under a dollar, not single-digit dollars.
- Median episode: ~15.4k tokens, 111 turns; **median Speaker Turn is only ~45
  tokens** — speaker-turn chunking (Stage 6) must merge turns, not split them.
- Flagged inventory resolved: 3 bonus episodes + 1 special (each with 2–4
  alias URLs), the crypto-series landing page (a stub), #98 (show notes only,
  no transcript published), #110/#114 (transcript-scale text but zero speaker
  labels — human call needed on whether it's transcript or notes).

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
