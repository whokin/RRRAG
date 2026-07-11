"""The Golden Set: evaluation questions pinned to their known source
episodes so retrieval success is mechanically checkable (CONTEXT.md).

Lives in the public repo — the questions are our own work product; no
verbatim transcript quotes (ADR-0001 posture). One JSON object per line:

  {"id": "hand-001", "question": "...",
   "source": {"series": "main", "episode": 101},
   "chunk_id": "101:20",              # optional, synthetic only
   "provenance": "hand",              # hand | synthetic | ama
   "notes": "..."}                    # optional

Cross-episode questions may pin multiple sources: "source" may be a list;
a retrieval hit on ANY pinned episode counts.
"""

import json
from pathlib import Path

GOLDEN_PATH = Path(__file__).parent / "golden.jsonl"
PROVENANCES = {"hand", "synthetic", "ama"}
SERIES = {"main", "crypto"}


def load() -> list[dict]:
    if not GOLDEN_PATH.exists():
        return []
    questions = []
    seen_ids = set()
    for line_no, line in enumerate(GOLDEN_PATH.read_text().splitlines(), 1):
        if not line.strip():
            continue
        q = json.loads(line)
        _validate(q, line_no)
        if q["id"] in seen_ids:
            raise ValueError(f"golden.jsonl:{line_no}: duplicate id {q['id']!r}")
        seen_ids.add(q["id"])
        questions.append(q)
    return questions


def sources(q: dict) -> list[dict]:
    src = q["source"]
    return src if isinstance(src, list) else [src]


def _validate(q: dict, line_no: int) -> None:
    where = f"golden.jsonl:{line_no}"
    for field in ("id", "question", "source", "provenance"):
        if field not in q:
            raise ValueError(f"{where}: missing {field!r}")
    if q["provenance"] not in PROVENANCES:
        raise ValueError(f"{where}: provenance must be one of {sorted(PROVENANCES)}")
    for src in sources(q):
        if src.get("series") not in SERIES or not isinstance(src.get("episode"), int):
            raise ValueError(f"{where}: source needs series in {sorted(SERIES)} and int episode")
