# Page Snapshots: fetch once, parse freely

The original rule "scrape once, never re-scrape; the raw JSON is the source of
truth" conflated two operations with very different costs. Fetching hits
rationalreminder.ca and is the thing we ethically want to do exactly once per
episode (ADR-0001); parsing turns HTML into an Episode Record and will
inevitably have bugs discovered late (old page formats, mangled speaker
labels). Making the parsed JSON the permanent artifact would force a choice
between living with corrupt Episode Records and re-hitting the site. Instead
we split the pipeline (the medallion pattern from data engineering): the
scraper saves every episode page's raw HTML as a **Page Snapshot** (bronze) in
`data/html/`, synced to R2 like all data; a separate parser derives Episode
Records (silver) in `data/raw/`, re-runnable forever without touching the
site; chunks and the Lance index (gold) are derived further downstream. The
alternative — parse-only, no HTML kept — saves ~100–200 MB of storage but
destroys the only artifact that can't be regenerated.
