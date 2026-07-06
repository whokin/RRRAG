# RRRAG

A learning project building a retrieval-augmented search tool over the Rational
Reminder podcast's accumulated knowledge. The learner's understanding is the
primary product; the hosted tool is the artifact.

## Language

### Corpus

**Episode**:
One installment of the Rational Reminder podcast, identified by its series
plus its number within that series (the main series is implied when
unstated; e.g. episode 416 vs. crypto episode 5). "C5"-style short forms are
a display convention, never a storage format.
_Avoid_: show, podcast (the podcast is the whole series)

**Page Snapshot**:
The raw HTML of one episode's page, fetched from the site once — re-fetched
only as a deliberate correction, never routinely. The permanent source of
truth from which Episode Records are derived.
_Avoid_: cache, raw HTML dump

**Refresh**:
The recurring run that discovers newly published episodes, diffs them against
the Manifest, and fetches/parses only what's new. Existing Page Snapshots are
untouched.
_Avoid_: re-scrape, sync (that's data syncing to R2)

**Episode Record**:
The structured record derived by parsing a Page Snapshot: metadata, summary,
key points, transcript, and reference links. Cheap to regenerate — parsing is
freely re-runnable; fetching is not.
_Avoid_: scrape, dump

**Speaker Turn**:
A contiguous stretch of transcript spoken by one identified person.
_Avoid_: utterance, dialogue line

**Key Point**:
A timestamped highlight published on the episode page by the show itself.
_Avoid_: highlight, bookmark

**Manifest**:
The per-episode status ledger: every discovered episode with its URL and
current state (discovered, fetched, parsed, flagged, backfilled, alias).
"Flagged episodes" is a filter over the Manifest, not a separate list.
_Avoid_: flag list, error log

**Alias**:
An alternate URL the show publishes for an existing Episode (topic or guest
slug); its content is identical to the canonical page, so it never becomes
its own Episode Record.
_Avoid_: duplicate, topic page

**Corpus**:
The full set of Episode Records.
_Avoid_: dataset (ambiguous with the golden set), archive

### Retrieval

**Chunk**:
The unit of text that gets embedded and retrieved. How Episode Records become
Chunks varies by Stage.
_Avoid_: passage, segment, document

**Citation**:
A reference attached to an answer that deep-links to a specific episode and
timestamp.
_Avoid_: source, footnote

### Learning

**Stage**:
One increment of the learning roadmap, always measured against the previous
Stage on the Golden Set.
_Avoid_: phase, milestone, step

**Experiment**:
Work in the sandbox comparing techniques; free to break, never deployed.
_Avoid_: prototype, spike

**Promotion**:
Moving a technique from the sandbox into the product after it wins on the
Golden Set.
_Avoid_: merge, graduation

**Golden Question**:
An evaluation question pinned to its known source episode(s), so retrieval
success is mechanically checkable.
_Avoid_: test case, query (a query is what a user types)

**Golden Set**:
The fixed collection of Golden Questions every Stage is measured against.
_Avoid_: benchmark, test suite
