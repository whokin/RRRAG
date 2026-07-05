# Learning Journal

One entry per concept or pattern, added in the session where it first mattered.
Format: what it is, why it showed up here, keywords to dig deeper.

## 2026-07-04 — Stage 0 planning

### Medallion architecture (bronze / silver / gold)
Layered data pipeline: keep the rawest capture immutable (bronze = Page
Snapshots), derive cleaned/structured data from it (silver = Episode Records),
derive analysis- or serving-ready data from that (gold = chunks + Lance
index). Each layer is regenerable from the one below; only bronze is
irreplaceable. Showed up as ADR-0006's "fetch once, parse freely."
_Dig deeper: medallion architecture (Databricks), ELT vs ETL, data lakehouse._

### Idempotent, separately re-runnable pipeline steps
`discover` / `fetch` / `parse` as three commands instead of one script: each
step can be re-run without side effects or re-doing upstream work. This is
what makes parser bugs cheap and the weekly Refresh trivial — re-running is
always safe.
_Dig deeper: idempotency, functional data engineering (Maxime Beauchemin),
checkpointing._

### Status ledger / manifest pattern
One record per work item with an explicit state machine
(discovered → fetched → parsed / flagged → backfilled) instead of scattered
logs or error lists. "Flagged episodes" is a *query* over the ledger, not a
separate artifact. Makes progress, gaps, and retries queryable.
_Dig deeper: state machines, workflow state tracking, task queues._

### Data contract / minimum viable record
Explicit required-vs-optional fields decide what enters the Corpus: transcript
text is required; speaker labels, summary, key points are optional enrichment
whose absence is *recorded*, not fatal. Validation gates belong at the
boundary where data enters the system.
_Dig deeper: data contracts, schema validation (pydantic), great expectations._

### EDA before feature commitment
Don't design Stage 5/6 speaker features before measuring how many episodes
even have speaker labels. Exploratory data analysis converts assumptions into
counts; features get sized to the data that actually exists.
_Dig deeper: exploratory data analysis, data profiling._

### Probe-first crawling (stratified sampling)
Before the full 430-episode crawl, scrape 5 episodes spanning the show's
history (#50, #150, #250, #350, #416) so the parser meets old formats
immediately, not at episode 380 of a long run. Choosing samples to span known
variation is stratified sampling in miniature.
_Dig deeper: stratified sampling, smoke testing, canary runs._

### Reproducible dev environments
All development inside a devcontainer built before the first line of code —
the environment is part of the repo, so "works on my machine" can't happen.
_Dig deeper: devcontainers, hermetic builds, Twelve-Factor App (dev/prod
parity)._

### Orchestration (queued for stretch)
The automated weekly Refresh will be built with Airflow — DAGs, scheduling,
retries, alerting, backfills — deliberately oversized for one weekly job,
chosen as the learning vehicle because it's the industry-standard
orchestrator.
_Dig deeper: Airflow DAGs, sensors, backfills; alternatives: Dagster, Prefect,
cron + GitHub Actions._
