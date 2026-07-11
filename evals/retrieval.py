"""Retrieval metrics against the Golden Set: hit-rate@k and MRR.

Zero LLM calls — only one Voyage query-embed per Golden Question. A "hit"
means a chunk from a pinned source episode appears in the top k; MRR uses
the rank of the first such chunk. These are the numbers every Stage 3+
technique must move (PLAN.md: measurement before enhancement).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from rag_core import index

from . import golden

RUNS_DIR = Path(__file__).parent / "runs"
K_VALUES = (1, 3, 5, 8)


def rank_of_first_hit(q: dict, rows: list[dict]) -> int | None:
    """1-based rank of the first retrieved chunk from any pinned episode."""
    pinned = {(s["series"], s["episode"]) for s in golden.sources(q)}
    for rank, row in enumerate(rows, 1):
        if (row["series"], row["episode"]) in pinned:
            return rank
    return None


def evaluate(k: int = max(K_VALUES)) -> dict:
    questions = golden.load()
    if not questions:
        raise SystemExit("golden.jsonl is empty — add Golden Questions first")
    per_question = []
    for q in questions:
        rows = index.search(q["question"], k=k)
        rank = rank_of_first_hit(q, rows)
        per_question.append({
            "id": q["id"],
            "provenance": q["provenance"],
            "rank": rank,
            "top_distance": round(rows[0]["_distance"], 4) if rows else None,
        })

    def aggregate(items: list[dict]) -> dict:
        n = len(items)
        return {
            "n": n,
            **{
                f"hit_rate@{kv}": round(
                    sum(1 for i in items if i["rank"] and i["rank"] <= kv) / n, 3
                )
                for kv in K_VALUES
                if kv <= k
            },
            "mrr": round(sum(1 / i["rank"] for i in items if i["rank"]) / n, 3),
        }

    by_provenance = {
        prov: aggregate(items)
        for prov in sorted({i["provenance"] for i in per_question})
        if (items := [i for i in per_question if i["provenance"] == prov])
    }
    return {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "k": k,
        "index_table": index.TABLE,
        "embedding_model": "voyage-3.5",
        "overall": aggregate(per_question),
        "by_provenance": by_provenance,
        "per_question": per_question,
    }


def save_run(result: dict, label: str) -> Path:
    RUNS_DIR.mkdir(exist_ok=True)
    date = result["at"][:10]
    path = RUNS_DIR / f"{date}-{label}.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    return path
