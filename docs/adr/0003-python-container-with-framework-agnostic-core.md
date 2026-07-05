# Python owns all RAG logic, deployed as a Cloudflare Container

The RAG learning ecosystem is overwhelmingly Python, but Cloudflare's native
runtime is TypeScript Workers. We keep Python end-to-end: all retrieval logic
lives in a plain, framework-agnostic `rag_core/` package (ports-and-adapters —
`Retriever`/`Reranker`/`Generator` interfaces, extracted when a Stage forces
them, not designed up front); FastAPI is a thin adapter deployed as a
Cloudflare Container; the frontend is a thin static site calling
`POST /api/query`. In prod, embeddings/reranking/LLM are hosted API calls so
the container stays lean; local models are allowed in experiments only.

Rejected: TypeScript end-to-end (swims against the RAG ecosystem where the
learning happens) and Python-for-experiments + TS-for-product (every promoted
technique would be reimplemented, and experiment results would no longer
describe the code that ships).
