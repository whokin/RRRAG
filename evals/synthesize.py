"""Synthetic Golden Questions: sample chunks, have an LLM write a question
each chunk answers, pin question -> chunk_id/episode automatically.

Two-step because generation runs on the host (claude -p, subscription):
  1. `evals synth-prompts` (container) -> data/synth/prompts.jsonl
  2. ./synth.sh (host)                 -> data/synth/answers.jsonl
  3. `evals synth-collect` (container) -> appends to evals/golden.jsonl

Vocabulary-leak guard: a generated question sharing a 6-word shingle with
its source chunk is rejected — verbatim phrasing makes retrieval trivially
easy and inflates scores (PLAN.md, eval strategy).
"""

import json
import random
import re
from pathlib import Path

import lancedb

from rag_core.index import INDEX_DIR, TABLE

from . import golden

SYNTH_DIR = Path("data/synth")
PROMPT_TEMPLATE = """\
You are helping build an evaluation set for a retrieval system over podcast \
transcripts (the Rational Reminder podcast, on investing and personal \
finance). Below is one transcript excerpt.

Write ONE question that a curious listener might genuinely ask, which this \
excerpt clearly answers. Requirements:
- Paraphrase: do NOT reuse distinctive multi-word phrases or rare terms \
verbatim from the excerpt.
- The question must stand alone — no "the excerpt", "the episode", "the guest".
- Under 30 words. Output ONLY the question text, nothing else.

Excerpt:
{text}"""


def _shingles(text: str, n: int = 6) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def make_prompts(n: int = 35, seed: int = 42) -> None:
    table = lancedb.connect(INDEX_DIR).open_table(TABLE)
    rows = table.to_arrow().to_pylist()
    # skip intro chunks (index 0 is usually boilerplate + banter)
    candidates = [r for r in rows if r["chunk_index"] > 0]
    random.Random(seed).shuffle(candidates)
    SYNTH_DIR.mkdir(parents=True, exist_ok=True)
    out = SYNTH_DIR / "prompts.jsonl"
    with out.open("w") as f:
        for r in candidates[:n]:
            f.write(json.dumps({
                "chunk_id": r["chunk_id"],
                "series": r["series"],
                "episode": r["episode"],
                "prompt": PROMPT_TEMPLATE.format(text=r["text"]),
            }, ensure_ascii=False) + "\n")
    print(f"synth: {n} prompts written to {out} — run ./synth.sh on the host next")


def collect() -> None:
    answers_path = SYNTH_DIR / "answers.jsonl"
    if not answers_path.exists():
        raise SystemExit(f"{answers_path} not found — run ./synth.sh first")
    table = lancedb.connect(INDEX_DIR).open_table(TABLE)
    chunk_text = {
        r["chunk_id"]: r["text"]
        for r in table.to_arrow().select(["chunk_id", "text"]).to_pylist()
    }
    existing = {q["id"] for q in golden.load()}
    added = rejected = 0
    with golden.GOLDEN_PATH.open("a") as out:
        for line in answers_path.read_text().splitlines():
            if not line.strip():
                continue
            a = json.loads(line)
            question = a["question"].strip().strip('"')
            qid = f"synthetic-{a['chunk_id'].replace(':', '-')}"
            if qid in existing:
                continue
            if _shingles(question) & _shingles(chunk_text[a["chunk_id"]]):
                print(f"synth: REJECTED {qid} — 6-word verbatim overlap with source chunk")
                rejected += 1
                continue
            out.write(json.dumps({
                "id": qid,
                "question": question,
                "source": {"series": a["series"], "episode": a["episode"]},
                "chunk_id": a["chunk_id"],
                "provenance": "synthetic",
            }, ensure_ascii=False) + "\n")
            added += 1
    print(f"synth: {added} questions appended to golden.jsonl, {rejected} rejected")
