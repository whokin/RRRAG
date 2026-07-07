# Weekend ritual targets (PLAN.md). All commands assume you're inside the
# devcontainer; nothing here depends on host tooling beyond make itself.

-include .env
export

# rclone remote "r2" defined entirely from .env — no rclone.conf needed
export RCLONE_CONFIG_R2_TYPE = s3
export RCLONE_CONFIG_R2_PROVIDER = Cloudflare
export RCLONE_CONFIG_R2_ACCESS_KEY_ID = $(R2_ACCESS_KEY_ID)
export RCLONE_CONFIG_R2_SECRET_ACCESS_KEY = $(R2_SECRET_ACCESS_KEY)
export RCLONE_CONFIG_R2_ENDPOINT = https://$(R2_ACCOUNT_ID).r2.cloudflarestorage.com

.PHONY: refresh status probe sync-data pull-data

refresh:  ## discover + fetch + parse anything newly published
	uv run scraper refresh

status:   ## Manifest summary
	uv run scraper status

probe:    ## the 5-episode probe spanning show history
	uv run scraper discover
	uv run scraper fetch --episodes 50,150,250,350,416
	uv run scraper parse --episodes 50,150,250,350,416

# rclone copy is additive (never deletes) — safe from any machine in either
# direction; the corpus is append-mostly. Deletions are deliberate manual acts.
sync-data:  ## upload data/ -> private R2 bucket (ADR-0001, ADR-0004)
	rclone copy data/ r2:$(R2_BUCKET)/data --progress --checksum

pull-data:  ## download R2 bucket -> data/ (fresh machine)
	rclone copy r2:$(R2_BUCKET)/data data/ --progress --checksum
