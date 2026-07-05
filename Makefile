# Weekend ritual targets (PLAN.md). All commands assume you're inside the
# devcontainer; nothing here depends on host tooling beyond make itself.

.PHONY: refresh status probe sync-data

refresh:  ## discover + fetch + parse anything newly published
	uv run scraper refresh

status:   ## Manifest summary
	uv run scraper status

probe:    ## the 5-episode probe spanning show history
	uv run scraper discover
	uv run scraper fetch --episodes 50,150,250,350,416
	uv run scraper parse --episodes 50,150,250,350,416

sync-data:  ## data/ <-> private R2 bucket (ADR-0001, ADR-0004)
	@echo "TODO: rclone sync against the private R2 bucket (not set up yet)"
