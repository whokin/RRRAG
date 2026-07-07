"""Voyage embeddings (hosted, per ADR-0003's lean-container rule).

voyage-3.5 as the general-purpose baseline; voyage-finance-2 is on the
ablation backlog. input_type matters: documents and queries are embedded
with different prompts so they land in compatible spaces."""

import voyageai

MODEL = "voyage-3.5"
BATCH_SIZE = 128


def embed_documents(texts: list[str]) -> list[list[float]]:
    client = voyageai.Client()  # reads VOYAGE_API_KEY
    vectors: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        result = client.embed(batch, model=MODEL, input_type="document")
        vectors.extend(result.embeddings)
        done = min(i + BATCH_SIZE, len(texts))
        print(f"embed: {done}/{len(texts)}", end="\r", flush=True)
    print()
    return vectors


def embed_query(text: str) -> list[float]:
    client = voyageai.Client()
    return client.embed([text], model=MODEL, input_type="query").embeddings[0]
