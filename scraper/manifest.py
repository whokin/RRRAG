"""The Manifest: per-episode status ledger (CONTEXT.md).

States: discovered -> fetched -> parsed | flagged -> backfilled.
"Flagged episodes" is a filter over the Manifest, not a separate list."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
MANIFEST_PATH = DATA_DIR / "manifest.json"
HTML_DIR = DATA_DIR / "html"
RAW_DIR = DATA_DIR / "raw"

STATUSES = ("discovered", "fetched", "parsed", "flagged", "backfilled", "alias")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load() -> dict[str, dict]:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text())


def save(manifest: dict[str, dict]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(dict(sorted(manifest.items())), indent=2, ensure_ascii=False) + "\n"
    )


def slug_of(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def infer_episode(slug: str) -> int | None:
    """Episode number from the URL slug; parse() refines it later.

    Only pure-numeric slugs count — 'crypto1' is NOT episode 1, and
    '388-x63ds' would collide with the real '388'."""
    return int(slug) if re.fullmatch(r"\d+", slug) else None


def new_entry(url: str) -> dict:
    slug = slug_of(url)
    return {
        "url": url,
        "slug": slug,
        "episode": infer_episode(slug),
        "status": "discovered",
        "discovered_at": now_iso(),
        "fetched_at": None,
        "parsed_at": None,
        "flags": [],
        "gaps": [],
    }


def select(
    manifest: dict[str, dict],
    episodes: list[int] | None = None,
    statuses: tuple[str, ...] | None = None,
) -> list[dict]:
    entries = manifest.values()
    if episodes is not None:
        entries = [e for e in entries if e["episode"] in episodes]
    if statuses is not None:
        entries = [e for e in entries if e["status"] in statuses]
    return sorted(entries, key=lambda e: (e["episode"] is None, e["episode"], e["slug"]))
