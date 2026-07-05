# LanceDB as the embedded vector store

The corpus is small (~50–65k chunks), so iteration speed and zero ops beat
managed scale. LanceDB runs identically in notebooks, the dev container, and
the production container; its native BM25 (Tantivy) + hybrid search maps
directly onto roadmap Stage 3; Lance files read straight from Cloudflare R2 in
prod; and native dataset versioning supports side-by-side index ablations.

Rejected: Chroma (hybrid/sparse support is its newest, least-proven feature;
wins only on community mindshare), Cloudflare Vectorize (Workers-oriented,
awkward from Python, needs a separate BM25 engine), hosted pgvector (external
dependency and network round-trips in every experiment loop; more
industry-realistic, kept as the reversible migration path behind `rag_core`'s
store interface). Full comparison: `resources/vector-databases-2026.md`.

Learning guard: Stage 3 implements reciprocal-rank fusion by hand before
comparing against LanceDB's built-in `.hybrid()`.
