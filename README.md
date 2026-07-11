# RRRAG

A learning project: a retrieval-augmented search tool over the [Rational
Reminder podcast](https://rationalreminder.ca/)'s accumulated knowledge,
built stage by stage from naive RAG to advanced techniques. My own
understanding is the primary product; the hosted tool is the artifact.

- [PLAN.md](PLAN.md) — the roadmap: dataset, learning stages, product
- [CONTEXT.md](CONTEXT.md) — the project glossary
- [docs/adr/](docs/adr/) — architecture decision records
- [docs/LEARNING.md](docs/LEARNING.md) — learning journal of concepts visited
- [CHANGELOG.md](CHANGELOG.md) — per-session log of what changed and what it found

**Note on data:** the corpus is scraped from rationalreminder.ca and is their
copyrighted content. It is never committed to this repo (see
[ADR-0001](docs/adr/0001-dataset-never-committed-publicly.md)); the product
links back to source episodes. This repo contains code and documentation only.

## Setup

All development happens inside the devcontainer (ADR-0004) — nothing depends
on tools installed on the host.

```bash
# open in the devcontainer (VS Code: "Reopen in Container", or GitHub Codespaces)
cp .env.example .env   # fill in R2 + Voyage + Anthropic credentials as needed
uv sync
```

`.env` values, and what needs them:

| Variable | Needed for |
|---|---|
| `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET` | `make sync-data` / `make pull-data` |
| `VOYAGE_API_KEY` | `rag index` (embeddings) |
| `ANTHROPIC_API_KEY` | `rag ask` (generation) — not needed for `rag index` or `rag search` |

On a fresh machine: `make pull-data` restores `data/` from R2 before running
anything else.

## Commands

**`scraper`** — sitemap → Manifest → Page Snapshots → Episode Records
(Stage 0; see PLAN.md's Pillar 1):

```bash
uv run scraper discover              # sitemap.xml -> Manifest
uv run scraper fetch                 # Manifest -> Page Snapshots (data/html/)
uv run scraper fetch --episodes 416  # fetch specific episodes only
uv run scraper parse                 # Page Snapshots -> Episode Records (data/raw/)
uv run scraper enrich                # derive attribution (inferred_speaker) into Episode Records
uv run scraper refresh               # discover + fetch + parse + enrich, new episodes only
uv run scraper status                # Manifest summary: counts by status, series, flagged episodes
```

**`rag`** — chunk → embed → index → answer (Stage 1):

```bash
uv run rag index               # chunk the corpus, embed via Voyage, write the LanceDB table
uv run rag index --limit 50    # smoke-test on the first 50 chunks
uv run rag search "covered calls"       # retrieval only, no LLM call — good for eyeballing
uv run rag ask "what does Ben think about covered calls?"   # needs ANTHROPIC_API_KEY
uv run rag prompt "..."        # print the stuffed prompt instead of calling the API
```

**`./ask.sh "question"`** (host, not container) — subscription pathway:
runs retrieval in the container via `rag prompt`, pipes the stuffed prompt
into the host's `claude -p` (billed to a Claude subscription). Same prompt
bytes as `rag ask`; human-in-the-loop experimentation only.

**`make`** targets wrap the above for the weekend ritual (see the
[Makefile](Makefile) for the R2 sync mechanics):

```bash
make probe       # the 5-episode probe spanning show history (#50/150/250/350/416)
make refresh     # scraper refresh
make status      # scraper status
make sync-data   # upload data/ -> R2
make pull-data   # download R2 -> data/ (fresh machine)
```

## Status

See PLAN.md's [Status](PLAN.md#status) checklist for the current stage.
Stage 0 (scraper + corpus) is done: 430 Episode Records, EDA notebook at
[experiments/corpus_stats.ipynb](experiments/corpus_stats.ipynb), data synced
to R2. Stage 1 (naive RAG) is in progress in [rag_core/](rag_core/).
