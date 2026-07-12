# RRRAG — Plan

A learning project: build a retrieval-augmented search tool over the Rational
Reminder podcast corpus, progressing from naive RAG to advanced techniques, with
my own understanding as the primary product and a usable hosted tool as the
artifact.

Three pillars: **the dataset**, **the learning roadmap**, **the product**.

## Governing principles

- **Evaluation-driven development.** The eval harness is built immediately after
  the naive baseline and before any enhancement. Every technique must show its
  isolated contribution on the same golden set (ablation mindset: one variable
  at a time).
- **Sandbox + product split.** Learning happens in `experiments/` (notebooks,
  free-form comparisons, every stage stays runnable). Only techniques that win
  on the eval get promoted into the product code. (ADR-0002)
- **Core roadmap ships the product; stretch stages upgrade it.** Stages 0–4 are
  core; the hosted product ships after Stage 4. Stages 5–7 are genuinely
  optional upgrades to a live app.
- **Learning journal.** `docs/LEARNING.md` accumulates the named concepts and
  patterns each session touches — one entry per concept, with why it mattered
  here and keywords to dig deeper. Reviewable as a map of everything visited.

## Pillar 1 — Dataset

**Source:** rationalreminder.ca episode pages (e.g. `/podcast/416`). Each page
already has metadata, a summary, timestamped key points, a speaker-labeled
transcript, and reference links — no speech-to-text needed. Site is Squarespace.
**Politeness settings:** sequential requests (no concurrency), fixed 2-second
delay, honest User-Agent identifying the project with contact email,
exponential backoff on 5xx, and immediate halt on 403/429 (a block signal
means reassess, never push through). Only episode pages are fetched.

**Format:** one JSON file per episode in gitignored `data/raw/`, capturing
everything, structured:

```json
{
  "series": "main",
  "episode": 416,
  "title": "...",
  "date": "2026-07-02",
  "speakers": ["Ben Wilson", "Benjamin Felix", "Dan Bortolotti"],
  "summary": "...",
  "key_points": [{"timestamp": "0:01:12", "text": "..."}],
  "transcript": [
    {"speaker": "Benjamin Felix", "text": "..."},
    {"speaker": null, "style": "answer", "inferred_speaker": "Guest Name", "text": "..."}
  ],
  "links": [{"title": "...", "url": "..."}],
  "source_url": "https://rationalreminder.ca/podcast/416"
}
```

(`speaker` is always the observed label as printed; `style` and
`inferred_speaker` are enrichment on unattributed turns — see CHANGELOG
2026-07-06 for the evidence-bounded attribution rules.)

**Rules:**
- The scraper is a **permanent, recurring tool**, not a one-off: after the
  initial crawl it runs as a weekly **Refresh** (new episodes only; existing
  Page Snapshots untouched). Deliberate per-episode correction re-fetches are
  allowed; routine re-fetching is not.
- **Fetch once, parse freely** (medallion architecture, ADR-0006). The scraper
  saves each episode page's raw HTML as a Page Snapshot in gitignored
  `data/html/` (synced to R2) — that is the permanent source of truth and the
  only step that touches the site. Episode Records in `data/raw/` are derived
  by a separate parser, re-runnable forever without re-fetching.
- Discovery via `sitemap.xml` (one polite request, the file published *for*
  crawlers), filtered to episode pages — no guessing URL patterns. This seeds
  the **Manifest**: a per-episode ledger (URL, episode identity, status:
  discovered → fetched → parsed / flagged → backfilled, plus alias for
  duplicate URLs of the same episode).
- **Minimum viable Episode Record:** episode identity (series + number within
  the series; main series implied, crypto series numbered from its titles),
  title, publish date, source URL, and transcript *text*. Everything else — Speaker Turns, summary,
  key points, guests, links — is optional enrichment; gaps are recorded in the
  Manifest (so coverage is queryable) but don't flag the episode. An unlabeled
  transcript stays in the Corpus: content beats attribution.
- Episodes missing a required field (old formats, PDF-era transcripts) are
  flagged in the Manifest for manual backfill — no heroics handling every
  historical layout.
- **Scraper layout:** top-level `scraper/` package — Pillar 1 tooling, neither
  `experiments/` nor product code. CLI subcommands mirror the pipeline:
  `discover` (sitemap → Manifest), `fetch` (Manifest → Page Snapshots),
  `parse` (Page Snapshots → Episode Records), `enrich` (derived attribution
  into Episode Records), `refresh` (all four, new episodes only), `status`
  (Manifest summary). httpx + BeautifulSoup, single root `pyproject.toml` (uv),
  Manifest at `data/manifest.json` (JSON, not SQLite — ~430 rows, eyeballable
  diffs).
- **Probe before crawl:** the first run covers 5 episodes spanning the show's
  history (#50, #150, #250, #350, #416) so the parser meets old formats
  immediately. Pass = every probe episode reaches a *correct* Manifest state
  (valid eyeballed Episode Record, or flagged for the right reason). The full
  crawl is conditional on the probe; if the probe passes, the full *fetch*
  (bronze only) runs even while parser work remains — collecting the
  irreplaceable layer never waits on the derivable one.
- The corpus-stats notebook does the EDA pass after the full crawl: field
  coverage per era, especially *how many episodes actually have speaker
  labels* — that number decides how much Stage 5/6 speaker-dependent work is
  even possible.
- The dataset is Rational Reminder's copyrighted content: **never committed to
  the public repo** (ADR-0001). Canonical home is a private Cloudflare R2
  bucket; any machine syncs it down via `make sync-data`.
- The product links back to source episodes (attribution + traffic to them).

## Pillar 2 — Learning roadmap

| Stage | Name | What gets built | What it teaches |
|-------|------|-----------------|-----------------|
| 0 | Dataset | Scraper, parsed corpus, corpus-stats notebook | Ingestion, data quality |
| 1 | Naive RAG | Fixed-size chunks → Voyage embeddings → LanceDB cosine top-k → stuff prompt → Claude answer | The baseline everything is measured against |
| 2 | **Eval harness** | Golden set (~50 questions), retrieval metrics (hit-rate, MRR), LLM-judged answer quality with a non-Claude judge | Measurement before enhancement — the load-bearing stage |
| 3 | Hybrid search | BM25 (LanceDB/Tantivy) + dense, **RRF implemented by hand**, then compared against LanceDB's built-in `.hybrid()` | Sparse vs dense retrieval; fusion. Financial jargon (tickers, "factor loading") is where keyword search should visibly win |
| 4 | Reranker | Cohere Rerank over fused candidates; compare vs a self-hosted cross-encoder in experiments | Two-stage retrieval, precision@k |
| — | **SHIP** | Product goes live on Cloudflare after Stage 4 | — |
| 5 | Query understanding | Query rewriting; metadata filters ("what did Ben say…" → speaker filter, "in episode 300" → episode filter) | Pre-retrieval intelligence. Builds the condense-question seam chat needs later |
| 6 | Structure-aware retrieval | Speaker-turn chunking, parent-document retrieval via summaries, timestamp deep-links in citations | Where this stops being a generic tutorial and becomes *this corpus's* RAG |
| 7 | Agentic loops | Query decomposition, iterative retrieve-and-refine, self-checking citations | Agent orchestration |

**Ablation backlog (run when curious, not blocking):** Voyage general vs
`voyage-finance-2` domain embeddings; chunk-size sweep; index versions v1
(fixed) vs v2 (speaker-turn) via Lance dataset versioning; recovering Speaker
Turns for unlabeled old transcripts via post-processing (LLM attribution from
context, or diarization from audio) if EDA shows a meaningful unlabeled
subset.

**Enhancement backlog (stretch):** automate the weekly Refresh end-to-end
(sitemap → fetch → parse → chunk → embed → index) orchestrated with
**Airflow** — deliberately oversized for one weekly job; chosen as a learning
vehicle for DAG orchestration, scheduling, retries, alerting, and backfills.
Only worth building once the full pipeline exists to automate. Until then,
Refresh is manual: `make refresh` in the weekend ritual, next to `git push`.

### Eval strategy (Stage 2 detail)

Golden set of ~50 questions, hybrid provenance:
- ~15 hand-written — including deliberately hard cross-episode questions
  ("how has Ben's view on covered calls evolved?").
- ~35 synthetic — LLM generates questions from randomly sampled chunks, each
  pinned to its source episode/chunk so retrieval hit-rate is mechanically
  checkable. Watch for vocabulary-leak bias inflating scores.
- Mine real listener questions from AMA episodes in the corpus — natural
  phrasings of what real users will type.

Metrics: retrieval hit-rate@k and MRR against pinned sources; answer
faithfulness/relevance via LLM-as-judge using a **different model family than
the generator**. Judge calls are cached aggressively — 50 questions × every
experiment is the one line item that adds up.

## Pillar 3 — Product

**Shape:** an **answer page** — query in, synthesized answer out, with
citations that deep-link to episode + timestamp, retrieved excerpts shown below
the answer. One-shot Q&A, no conversation memory.

**Architecture (ADR-0003):**
- `rag_core/` — plain, framework-agnostic Python package. Ports-and-adapters:
  `Retriever` / `Reranker` / `Generator` interfaces; roadmap stages are
  swappable implementations. Interfaces get extracted when Stage 2+ forces
  them, not designed up front.
- `api/` — thin FastAPI adapter over `rag_core`, `POST /api/query`, deployed as
  a Cloudflare Container.
- `web/` — thin static frontend on Cloudflare, calling the API. The answer
  block is a self-contained component (so a future chat UI is a list of them).
- Vector store: **LanceDB embedded** (see `resources/vector-databases-2026.md`
  and ADR-0005). Index files read directly from R2 in prod.
- Hosted models: Voyage (embeddings), Cohere (rerank), Claude (generation).
  All behind `rag_core` interfaces. Local models allowed in experiments only —
  the container stays lean.

**Access:** gated behind Cloudflare Access at launch (me + invited friends).
Flip to public-with-defenses later only if wanted: rate limiting + Turnstile +
hard daily spend cap that degrades the app to search-only mode.

**Chat later (stretch):** cheap by design — client-side history sent per
request (container stays stateless), `POST /api/query` body grows an optional
`history` field (backward-compatible), Stage 5's query-rewriting step doubles
as the condense-question step. Estimated a weekend or two after the roadmap.
Do NOT build chat infrastructure early.

## Development workflow

**Multi-machine (ADR-0004):** code → GitHub (end every session with a push,
WIP branches welcome), data → private R2 (`make sync-data`), environment →
devcontainer. Repo lives at `~/Projects/RRRAG`, outside OneDrive.

**Dev container:** single container — Python 3.12 + uv, Node for the frontend.
No service containers needed (LanceDB is embedded; there is no database
server). GitHub Codespaces runs the same config in a browser as an escape
hatch on locked-down machines. **All development happens inside the container
from day one** — it is built before the first line of scraper code, so nothing
ever depends on tools that happen to exist on one machine; anyone cloning the
repo gets a working environment from the repo alone.

**Local-first testing, three tiers:**
1. **Inner loop** — dev container: notebooks, unit tests, uvicorn, local Lance
   files, frontend dev server. 95% of time here. Only model APIs are remote.
2. **Prod-parity** — `docker build` the actual deploy image locally, run it
   pointed at real R2. Catches packaging/index-loading issues pre-deploy.
3. **Cloudflare** — smoke test only: preview deploy, run a handful of golden
   questions to verify platform wiring.

**Design rule:** the app must not know it's on Cloudflare. All environment
differences arrive as env vars (`.env` locally, Cloudflare secrets in prod).
Any "am I in prod?" branch is a review smell.

**CI/CD (standard defaults, not grilled):** GitHub Actions — lint + tests on
PR; on merge to main, build container and deploy API + static site via
wrangler, behind a manual approval initially.

## Costs

- Embedding the full corpus (measured: 430 episodes, 10,195 chunks, ~8M
  tokens): $0 — well inside Voyage's 200M free-token grant; a full rebuild
  takes ~2 minutes at standard rate limits. (Planning guess was 50–65k
  chunks / 15–20M tokens — see LEARNING.md, "measure, don't extrapolate".)
- Per-query: cents. Access-gating makes abuse a non-problem at launch.
- Watch: eval runs (mitigated by caching judge calls).
- Fixed monthly: ~zero (embedded store, static frontend, one small container).

## Learning protocol ledger

Open items from CLAUDE.md's learning protocol. Checked at every session
start; the predict-gate hook (.claude/hooks/predict_gate.py) greps this
file for open predictions before letting an eval run. Entry formats
(exact prefixes matter — the hook matches on `- PREDICTION`):

    - PREDICTION (open): <experiment> — <number + confidence> (YYYY-MM-DD)
    - QUIZ OWED: <component> (built YYYY-MM-DD)

Clear a line by deleting it once resolved (prediction compared against
the result / quiz paid at a session start); don't let lines go stale.

_Nothing outstanding as of 2026-07-12._

## Status

- [x] Planning grilled and written (2026-07-04)
- [x] Stage 0 — scraper + corpus (2026-07-07: 430 Episode Records, EDA
      notebook, attribution enrichment, data in R2)
- [x] Stage 1 — naive RAG (2026-07-11: 10,195-chunk chunks_v1 index,
      retrieval + generation verified on the three-question test; API path
      awaits credits — subscription pathway via `ask.sh` meanwhile)
- [ ] Stage 2 — eval harness (in progress: evals/ package + 35 synthetic
      Golden Questions done; hand-written questions, AMA curation, and the
      baseline run are queued in docs/sessions/ briefs 02–03)
- [ ] Stage 3 — hybrid search
- [ ] Stage 4 — reranker → **ship**
- [ ] Stages 5–7 — stretch
