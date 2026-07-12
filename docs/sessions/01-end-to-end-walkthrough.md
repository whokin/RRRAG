# Session brief 01 — End-to-end walkthrough (user drives)

**Goal:** the user can explain every pipeline stage and run each by hand —
scaffolding, data flow, and how the pieces connect. No new features, no
refactors, no fixes unless something is actually broken.

**Read first:** CHANGELOG.md (top 3 entries), PLAN.md §Status, CONTEXT.md.

**Shape of the session:** Claude is the guide, the user is at the wheel.
For each stage: (1) user predicts what the command will do and what its
inputs/outputs are, (2) user runs it, (3) user explains what happened in
their own words, Claude corrects. Suggested route, in pipeline order:

1. `make pull-data` dry-run discussion (what would a fresh machine need?)
2. `uv run scraper status` — read the Manifest; find a flagged episode and
   explain WHY it's flagged from its Manifest entry
3. Pick one episode: open its Page Snapshot (bronze), its Episode Record
   (silver), find its chunks in the index (gold) — trace one sentence
   through all three layers
4. `uv run rag search "..."` — read distances; what makes a good vs weak hit
5. `./ask.sh "..."` — where does the prompt come from? (rag_core/answer.py
   build_prompt); why are API path and subscription path byte-identical?
6. `uv run evals retrieval --no-save` (will fail-fast or run on synthetic
   questions only — explain what it measures WITHOUT running the numbers
   story yet; the baseline ceremony belongs to session 03)
7. Open data/traces.jsonl — what would you use this for when an answer is
   bad? (failure isolation: retrieval vs generation vs judge)

**Done when:** the user can sketch the pipeline from memory (bronze →
silver → gold → retrieval → generation, with the Manifest and eval harness
attached in the right places) and writes their own docs/LEARNING.md entry
about whatever surprised them. Per the learning protocol, Claude quizzes
2–3 questions at the end.
