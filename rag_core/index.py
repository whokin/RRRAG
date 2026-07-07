"""LanceDB index (embedded, ADR-0005). Table chunks_v1 lives in data/index/
— gitignored, R2-synced like all data. ~10k rows: brute-force cosine search
is fine, no ANN index needed."""

from pathlib import Path

import lancedb

from . import chunks, embeddings

INDEX_DIR = Path("data/index")
TABLE = "chunks_v1"


# commit every N chunks so a crashed long run resumes instead of restarting
COMMIT_EVERY = 120


def build(limit: int | None = None, rebuild: bool = False) -> None:
    rows = chunks.corpus_chunks(limit=limit)
    db = lancedb.connect(INDEX_DIR)
    table = None
    if TABLE in db.table_names():
        if rebuild:
            db.drop_table(TABLE)
        else:
            table = db.open_table(TABLE)
            existing = set(table.to_arrow().column("chunk_id").to_pylist())
            rows = [r for r in rows if r["chunk_id"] not in existing]
            print(f"index: resuming — {len(existing)} rows present, {len(rows)} to embed")
    if table is None:
        print(f"index: {len(rows)} chunks to embed with {embeddings.MODEL}")
    for i in range(0, len(rows), COMMIT_EVERY):
        part = rows[i : i + COMMIT_EVERY]
        vectors = embeddings.embed_documents([r["text"] for r in part])
        for row, vector in zip(part, vectors):
            row["vector"] = vector
        if table is None:
            table = db.create_table(TABLE, part)
        else:
            table.add(part)
        print(f"index: {min(i + COMMIT_EVERY, len(rows))}/{len(rows)} committed")
    total = table.count_rows() if table is not None else 0
    print(f"index: {TABLE} at {INDEX_DIR} now has {total} rows")


def search(query: str, k: int = 8) -> list[dict]:
    db = lancedb.connect(INDEX_DIR)
    table = db.open_table(TABLE)
    vector = embeddings.embed_query(query)
    return table.search(vector).metric("cosine").limit(k).to_list()
