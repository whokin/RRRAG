# Vector Databases for RAG in 2026

## Quick Recommendation
**DECIDED (July 2026): LanceDB.** See "RRRAG Decision" below for rationale. (Earlier draft of this note said "Chroma or LanceDB to start, graduate to pgvector if scaling" — superseded.)

## The Landscape

### Chroma
- **Best for**: Prototyping, getting started quickly
- **Design**: Python-native, embedded (no server), zero-copy data access
- **Scale**: ~30% of prototypes ship on Chroma; rest migrate when scale grows
- **Setup time**: ~10 lines of code to insert and query vectors
- **Trade-offs**: Simple for small data; migrations exist when you outgrow it

### LanceDB
- **Best for**: Embedded systems with growth room, multi-modal data, versioning
- **Design**: Built on Lance columnar format, in-process, handles larger-than-memory datasets
- **Scale**: Better than Chroma for scaling embedded
- **Setup time**: Nearly as simple as Chroma
- **Full-text & hybrid**: Native BM25 full-text search (Tantivy) plus first-class hybrid
  query + rerank. Chroma only added sparse-vector/hybrid support in Oct 2025 — it works,
  but it's the newest part of Chroma's stack vs. core to LanceDB's identity
- **Object storage**: Lance files read directly from S3-compatible storage, including
  Cloudflare R2 — a prod container can open the index straight from R2, no copy step
- **Versioning**: Lance format versions datasets natively — index v1 (fixed chunks) and
  v2 (speaker-turn chunks) can coexist for ablation comparisons
- **Trade-offs**: Less community momentum than Chroma (fewer tutorials/SO answers), but
  technically superior for growing workloads

### pgvector (PostgreSQL Extension)
- **Best for**: Production RAG, boring-but-right default
- **Design**: Runs on your existing Postgres; no separate database to manage
- **Scale**: Comfortably handles 50M+ vectors
- **Advantages**: Operational simplicity (one database instead of two), all 2026 guides agree it's the production default
- **Migration path**: Most projects graduate here from embedded options
- **Trade-offs**: Requires Postgres infrastructure; slightly slower than dedicated vector DBs at extreme scale

### Qdrant
- **Best for**: Dedicated vector search at scale, rich metadata filtering
- **Design**: Open-source, written in Rust, purpose-built for vectors
- **Scale**: Excellent performance benchmarks in 2026
- **Advantages**: Rich query API, excellent metadata filtering, strong performance
- **Trade-offs**: More operational overhead than pgvector; overkill unless you need that performance

### Milvus & Weaviate
- **Milvus**: Billion-scale vector search, enterprise deployments
- **Weaviate**: Hybrid search (vector + keyword), GraphQL API
- **Trade-off**: Both overkill for most RAG projects; only needed at massive scale

## Key Insights from 2026

1. **The typical journey**: Prototype in Chroma → 70% migrate to pgvector for production
2. **pgvector consensus**: 2026 guides now call it the best default for RAG (not Chroma)
3. **Embedded vs. Managed**: If you already have Postgres, skip the separate vector DB entirely
4. **Deployment shape matters**: Edge/desktop apps → LanceDB; backend services → pgvector or Qdrant

## RRRAG Decision (July 2026): LanceDB

Confirmed during planning. Supersedes the earlier "start with Chroma" strategy below.

**Why LanceDB over Chroma for this specific roadmap:**
1. **Hybrid search is roadmap Stage 3.** LanceDB's BM25 (Tantivy) + vector in one store
   means no bolt-on keyword engine. Chroma's hybrid support (Oct 2025) is its newest,
   least-proven feature.
2. **Deployment shape.** Product is a Python FastAPI app in a Cloudflare Container;
   Lance reads indexes directly from R2 (S3-compatible). No index-copying step.
3. **Ablation workflow.** Native dataset versioning maps onto eval-every-stage: keep
   index variants side by side and compare on the same golden questions.
4. **Corpus is tiny** (~50-65k chunks) — pgvector's scale advantages solve a problem
   RRRAG doesn't have; embedded keeps iteration loops instant and monthly cost ~zero.

**What Chroma genuinely wins:** community mindshare — more tutorials and Stack Overflow
answers when stuck. Accepted trade-off.

**Learning caveat:** LanceDB's one-call `.hybrid()` is too convenient. Stage 3 plan:
implement reciprocal-rank fusion manually (separate vector + BM25 queries, fuse by hand),
*then* compare against LanceDB's built-in as a sanity check. Same technique, twice the
learning.

**Migration hedge (kept from original strategy):** keep store access behind a thin
interface in `rag_core/` so a later swap to pgvector stays reversible.

**Storage caveat — now load-bearing**: Don't store LanceDB data files inside
OneDrive-synced folders, and the RRRAG repo itself lives inside OneDrive
(`~/Library/CloudStorage/OneDrive-Personal/...`). Embedded databases don't love cloud
sync. Point the persistence directory outside cloud sync (or move the repo out of
OneDrive entirely — see dev-container planning).

## Sources
- [Zilliz: Chroma vs LanceDB comparison](https://zilliz.com/comparison/chroma-vs-lancedb)
- [LanceDB: Hybrid search with BM25 + semantic](https://www.lancedb.com/blog/hybrid-search-combining-bm25-and-semantic-search-for-better-results-with-lan-1358038fe7e6)
- [TECHSY: Best Vector Databases 2026](https://techsy.io/en/blog/best-vector-databases-2026)
- [Encore: Best Vector Databases in 2026](https://encore.dev/articles/best-vector-databases)
- [Qdrant vs Chroma 2026: Best Vector DB for RAG?](https://www.kunalganglani.com/blog/qdrant-vs-chroma)
- [4xxi: Vector Database Comparison 2026](https://4xxi.com/articles/vector-database-comparison/)
- [CallSphere: Vector Database Benchmarks 2026](https://callsphere.ai/blog/vector-database-benchmarks-2026-pgvector-qdrant-weaviate-milvus-lancedb)
