# CLAUDE.md — RRRAG

A learning project: the user's understanding is the primary product; the
hosted RAG tool is the artifact. Read `CHANGELOG.md` (latest entries) and
`PLAN.md` (§Status) before doing anything; `CONTEXT.md` is the glossary and
its terms are binding. Planned session work lives in `docs/sessions/`.

## Learning protocol (agreed 2026-07-11 — follow it, don't ask again)

1. **Slow down at learning-dense code.** Before implementing anything
   concept-heavy (metrics, chunking strategies, fusion, judge rubrics),
   explain what is being built and why, and confirm the user's
   understanding before proceeding. Plumbing (CLI wiring, docker, parsing)
   can move fast without ceremony.
2. **Predict-before-reveal.** Before any measurement or experiment runs,
   ask the user for a written prediction of the outcome; run it; compare
   explicitly against their prediction.
3. **The user writes docs/LEARNING.md.** When a journal-worthy concept
   comes up, prompt them to explain it in their own words, correct the
   explanation, then let them write the entry (offer optional dig-deeper
   pointers). Never write entries for them.
4. **Quiz checkpoints.** After building a component, ask 2–3 pointed
   questions about its design to gauge understanding before moving on.

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
