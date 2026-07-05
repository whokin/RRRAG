# RRRAG

A learning project: a retrieval-augmented search tool over the [Rational
Reminder podcast](https://rationalreminder.ca/)'s accumulated knowledge,
built stage by stage from naive RAG to advanced techniques. My own
understanding is the primary product; the hosted tool is the artifact.

- [PLAN.md](PLAN.md) — the roadmap: dataset, learning stages, product
- [CONTEXT.md](CONTEXT.md) — the project glossary
- [docs/adr/](docs/adr/) — architecture decision records
- [docs/LEARNING.md](docs/LEARNING.md) — learning journal of concepts visited

**Note on data:** the corpus is scraped from rationalreminder.ca and is their
copyrighted content. It is never committed to this repo (see
[ADR-0001](docs/adr/0001-dataset-never-committed-publicly.md)); the product
links back to source episodes. This repo contains code and documentation only.
