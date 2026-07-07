"""LanceDB index (embedded, ADR-0005). Table chunks_v1 lives in data/index/
— gitignored, R2-synced like all data. ~10k rows: brute-force cosine search
is fine, no ANN index needed."""

from pathlib import Path

import lancedb

from . import chunks, embeddings

INDEX_DIR = Path("data/index")
TABLE = "chunks_v1"


def build(limit: int | None = None) -> None:
    rows = chunks.corpus_chunks(limit=limit)
    print(f"index: {len(rows)} chunks to embed with {embeddings.MODEL}")
    vectors = embeddings.embed_documents([r["text"] for r in rows])
    for row, vector in zip(rows, vectors):
        row["vector"] = vector
    db = lancedb.connect(INDEX_DIR)
    db.create_table(TABLE, rows, mode="overwrite")
    print(f"index: {TABLE} written to {INDEX_DIR} ({len(rows)} rows)")


def search(query: str, k: int = 8) -> list[dict]:
    db = lancedb.connect(INDEX_DIR)
    table = db.open_table(TABLE)
    vector = embeddings.embed_query(query)
    return table.search(vector).metric("cosine").limit(k).to_list()
