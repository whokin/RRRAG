"""Voyage embeddings (hosted, per ADR-0003's lean-container rule).

voyage-3.5 as the general-purpose baseline; voyage-finance-2 is on the
ablation backlog. input_type matters: documents and queries are embedded
with different prompts so they land in compatible spaces."""

import time

import voyageai
from voyageai import error as voyage_error

MODEL = "voyage-3.5"
BATCH_SIZE = 128
# Voyage without a payment method: 3 RPM / 10K TPM. TPM is the binding
# constraint: one ~9.6K-token batch per minute, nothing faster.
FREE_TIER_BATCH = 12
FREE_TIER_DELAY = 62.0


def embed_documents(texts: list[str]) -> list[list[float]]:
    client = voyageai.Client(max_retries=0)  # reads VOYAGE_API_KEY
    vectors: list[list[float]] = []
    batch_size, delay = BATCH_SIZE, 0.0
    i = 0
    while i < len(texts):
        batch = texts[i : i + batch_size]
        try:
            result = client.embed(batch, model=MODEL, input_type="document")
        except voyage_error.RateLimitError:
            if batch_size > FREE_TIER_BATCH:
                batch_size, delay = FREE_TIER_BATCH, FREE_TIER_DELAY
                print("embed: rate-limited — dropping to free-tier pacing "
                      f"({batch_size}/batch, {delay:.0f}s delay)")
            else:
                time.sleep(25)
            continue
        vectors.extend(result.embeddings)
        i += len(batch)
        print(f"embed: {i}/{len(texts)}", end="\r", flush=True)
        if delay and i < len(texts):
            time.sleep(delay)
    print()
    return vectors


def embed_query(text: str) -> list[float]:
    client = voyageai.Client()
    return client.embed([text], model=MODEL, input_type="query").embeddings[0]
