# Session brief 03 — Predictions, then the naive baseline

**Goal:** the Stage 2 exit ceremony — user commits to written predictions,
then the baseline runs, then prediction vs reality gets discussed and
recorded. Requires session 02's Golden Set to be complete.

**Read first:** CHANGELOG.md, evals/retrieval.py (understand hit-rate@k and
MRR before predicting — learning-dense, slow down here).

**Process:**
1. User writes predictions BEFORE anything runs, recorded verbatim in this
   file under "Predictions" below: hit-rate@8 and MRR, separately for hand
   / synthetic / ama provenances, plus one sentence of reasoning each
   (e.g. "synthetic will beat hand because...").
2. Run `uv run evals retrieval --label baseline-naive`.
3. Compare against predictions; discuss where and WHY they diverged.
4. User writes the docs/LEARNING.md entry; Claude quizzes (e.g. why is MRR
   more informative than hit-rate@1? what does a hand-vs-synthetic gap
   actually measure?).
5. Record headline numbers in CHANGELOG; commit evals/runs/ output; push.

This baseline is the bar every Stage 3+ technique must beat — treat the
numbers as the project's most load-bearing artifact after the corpus.

## Predictions (fill in before running — do not peek at results first)

- hand:      hit@8 = ____   mrr = ____   because:
- synthetic: hit@8 = ____   mrr = ____   because:
- ama:       hit@8 = ____   mrr = ____   because:
