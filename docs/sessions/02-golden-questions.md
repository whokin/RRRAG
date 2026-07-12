# Session brief 02 — Co-write the hand-written Golden Questions

**Goal:** ~15 hand-written Golden Questions (provenance "hand") plus a few
curated AMA questions (provenance "ama") appended to evals/golden.jsonl.
35 synthetic questions already exist there.

**Read first:** CHANGELOG.md (top entries), evals/golden.py docstring
(schema), PLAN.md §Eval strategy.

**Tags:** `[concept]` — question design and the vocabulary-leak reasoning
(user sketches first); `[plumbing]` — the jsonl mechanics and AMA
extraction.

**Process (agreed):** fully co-written — the user supplies topics or rough
phrasings a real listener would ask; Claude proposes final wording, pins
the source episode(s) via `rag search` + the Manifest, and the user
approves each line before it's written.

**Guidelines:**
- Natural listener phrasing, not transcript vocabulary (the synthetic set
  already skews toward corpus wording; hand questions are the antidote).
- Include 2–3 deliberately hard cross-episode questions (multi-source
  pinning is supported: "source" may be a list) — the naive baseline is
  EXPECTED to do poorly on these; that gap is what Stages 3–6 must close.
- AMA mining: episodes 337, 339, 345, 349, 353, 357, 362, 367, 379, 383,
  388 contain listener questions read aloud; extract candidates, paraphrase
  lightly, pin to the AMA episode that answers them.

**Done when:** golden.jsonl has ~50 questions across three provenances,
validated by `uv run evals retrieval --no-save > /dev/null` exiting
cleanly (stdout discarded on purpose — the numbers are session 03's
reveal; the predict-gate hook exempts `--no-save` for exactly this
validation), and the user can articulate why vocabulary leak inflates
retrieval scores.
