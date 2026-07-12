#!/usr/bin/env bash
# Host-side step 2 of synthetic Golden Question generation: pipe each
# prompt from data/synth/prompts.jsonl through claude -p (subscription,
# human-in-the-loop) and collect data/synth/answers.jsonl.
set -euo pipefail
python3 - <<'PY'
import json, subprocess, sys
from pathlib import Path

prompts = Path("data/synth/prompts.jsonl")
answers = Path("data/synth/answers.jsonl")
done = set()
if answers.exists():
    done = {json.loads(l)["chunk_id"] for l in answers.read_text().splitlines() if l.strip()}

lines = [json.loads(l) for l in prompts.read_text().splitlines() if l.strip()]
todo = [p for p in lines if p["chunk_id"] not in done]
print(f"{len(todo)} prompts to run ({len(done)} already answered)")
with answers.open("a") as out:
    for i, p in enumerate(todo, 1):
        q = subprocess.run(
            ["claude", "-p"], input=p["prompt"], capture_output=True, text=True, timeout=300
        ).stdout.strip()
        if not q:
            print(f"[{i}/{len(todo)}] {p['chunk_id']}: EMPTY — skipped", file=sys.stderr)
            continue
        out.write(json.dumps({
            "chunk_id": p["chunk_id"], "series": p["series"],
            "episode": p["episode"], "question": q,
        }, ensure_ascii=False) + "\n")
        out.flush()
        print(f"[{i}/{len(todo)}] {p['chunk_id']}: {q[:80]}")
PY
