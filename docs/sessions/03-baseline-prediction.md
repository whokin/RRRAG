# Session brief 03 — Predictions, then the naive baseline

**Goal:** the Stage 2 exit ceremony — user commits to written predictions,
then the baseline runs, then prediction vs reality gets discussed and
recorded. Requires session 02's Golden Set to be complete.

**Read first:** CHANGELOG.md, evals/retrieval.py (understand hit-rate@k and
MRR before predicting — learning-dense, slow down here).

**Tags:** `[concept]` throughout — this session IS the prediction ceremony.
Per the revised protocol, the user sketches how hit-rate@k and MRR work in
their own words before step 1, and each predicted number carries a
confidence level.

**Process:**
1. User writes predictions BEFORE anything runs, recorded verbatim in this
   file under "Predictions" below: hit-rate@8 and MRR (each with a
   confidence level), separately for hand / synthetic / ama provenances,
   plus one sentence of reasoning each (e.g. "synthetic will beat hand
   because..."). Also add a summary line to PLAN.md's Learning protocol
   ledger — `- PREDICTION (open): baseline-naive — …` — which is what the
   predict-gate hook checks before letting step 2 run.
2. Run `uv run evals retrieval --label baseline-naive`.
3. Compare against predictions; discuss where and WHY they diverged; clear
   the ledger's PREDICTION line.
4. User writes the docs/LEARNING.md entry. Add `- QUIZ OWED: retrieval
   metrics (hit-rate@k, MRR) + Golden Set design` to the ledger — the quiz
   itself happens at the NEXT session's start (spaced, per protocol), e.g.
   why is MRR more informative than hit-rate@1? what does a
   hand-vs-synthetic gap actually measure?
5. Record headline numbers in CHANGELOG; commit evals/runs/ output; push.

This baseline is the bar every Stage 3+ technique must beat — treat the
numbers as the project's most load-bearing artifact after the corpus.

**Spoiler note (2026-07-11):** the synthetic-only numbers were accidentally
revealed during the doc-audit smoke test — synthetic n=35: hit@8 = 0.857,
MRR = 0.668, with 5 complete misses. Predictions below therefore focus on
the unspoiled parts: the hand and ama provenances, and whether each beats
or trails synthetic (and why). Also worth predicting: what's wrong with the
5 synthetic questions that missed entirely?

## Predictions (fill in before running — do not peek at results first)

- hand:      hit@8 = ____   mrr = ____   vs synthetic (higher/lower): ____   because:
- ama:       hit@8 = ____   mrr = ____   vs synthetic (higher/lower): ____   because:
- the 5 synthetic complete-misses are probably failing because: ____
