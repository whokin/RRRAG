# CLAUDE.md — RRRAG

A learning project: the user's understanding is the primary product; the
hosted RAG tool is the artifact. Read `CHANGELOG.md` (latest entries) and
`PLAN.md` (§Status) before doing anything; `CONTEXT.md` is the glossary and
its terms are binding. Planned session work lives in `docs/sessions/`.

## Learning protocol (agreed 2026-07-11, revised 2026-07-12 — follow it, don't ask again)

**Session start, every session:** after the CHANGELOG / PLAN.md §Status
read, check PLAN.md's "Learning protocol ledger". Pay any `QUIZ OWED`
lines (2–3 pointed design questions, then clear the line), then ask one
retrieval question from an *older* docs/LEARNING.md entry — previous
sessions, not the most recent (spaced retrieval). Then start the work.

**Classification:** session briefs in docs/sessions/ tag tasks `[concept]`
(metrics, chunking, fusion, judge rubrics, retrieval/index and embedding
design) or `[plumbing]` (CLI wiring, docker, parsing) when the brief is
written — the density call happens at plan time, not mid-flow. Untagged
ad-hoc work: state the tag out loud before coding. `[plumbing]` moves
fast. `[concept]` follows the rules below and is never delegated to a
subagent — if a subagent contributes anyway, the sketch and quiz still
happen in the main thread.

1. **User sketches first at [concept] work.** Before implementing, ask
   the user to sketch the design in their own words (how would you
   compute this? what could go wrong?); correct the sketch; then build.
   Prefer plan mode here — its approval step is the understanding gate.
2. **Predict-before-reveal.** Before any measurement or experiment runs,
   the user writes a prediction with a number and a confidence level;
   record it as a `- PREDICTION (open): …` ledger line; run; compare
   explicitly; clear the line. A PreToolUse hook
   (.claude/hooks/predict_gate.py) blocks eval runs while the ledger
   holds no open prediction — that block is the protocol working, not an
   error to route around.
3. **The user writes docs/LEARNING.md.** When a journal-worthy concept
   comes up, prompt them to explain it in their own words, correct the
   explanation, then let them write the entry (offer optional dig-deeper
   pointers). Never write entries for them — not even a draft they
   approve; the writing is the point. The end-of-session CHANGELOG
   update includes the check: any entries owed?
4. **Quiz checkpoints are spaced.** The moment a `[concept]` component is
   built, add `- QUIZ OWED: …` to the ledger. The quiz itself happens at
   the *next* session's start (see above), not immediately — delayed
   retrieval is the point, and an immediate quiz mostly measures fluency.

**Warning sign (the 2026-07-11 failure shape):** several concept-dense
files changing in one pass with no dialogue in between. Notice it, stop,
back-fill the skipped sketch, check the ledger before continuing.

## Practices

- All development runs inside the devcontainer (`docker run … rrrag-dev`);
  nothing depends on host tooling. See README for commands.
- `data/` is never committed (ADR-0001); sync via `make sync-data` /
  `make pull-data` (R2). End every session with a git push (ADR-0004).
- One variable at a time: no enhancement work without the eval harness
  measuring it (PLAN.md governing principles).
- Update CHANGELOG.md before the session ends; glossary changes go to
  CONTEXT.md; decisions that are hard to reverse + surprising + a real
  trade-off get an ADR.
