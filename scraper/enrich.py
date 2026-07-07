"""enrich: derived attribution written into Episode Records, freely
re-runnable (silver-layer enrichment; ADR-0006 semantics apply).

The only inference with strong evidence (validated 2026-07-06 across all 143
interview-style episodes): answer-style turns belong to the episode's single
guest, whose name is in the title (142/143 extractable, 0 multi-guest,
first-name addressing corroborates 113/142). Question turns stay
unattributed — 101/143 episodes carry no in-episode evidence of which hosts
were present, and we don't assert what the page doesn't support. The
observed `speaker` field is never touched."""

import json
import re

from . import manifest

HONORIFIC = re.compile(r"^(prof\.?|professor|dr\.?|mr\.?|ms\.?)\s+", re.I)
TITLE_GUEST = re.compile(
    r"(?:episode\s+\d+|understanding crypto\s+\d+)\s*[:\-–—]\s*([^:]+?)\s*[:\-–—]", re.I
)


def guest_from_title(title: str | None) -> str | None:
    m = TITLE_GUEST.match(title or "")
    if not m:
        return None
    guest = HONORIFIC.sub("", m.group(1).strip())
    if not re.match(r"^[A-Z]", guest) or len(guest.split()) > 5:
        return None
    return guest


def run(episodes: list[int] | None = None) -> None:
    m = manifest.load()
    targets = manifest.select(m, episodes=episodes, statuses=("parsed",))
    enriched_eps = enriched_turns = 0
    for entry in targets:
        path = manifest.RAW_DIR / f"{entry['slug']}.json"
        record = json.loads(path.read_text())
        guest = guest_from_title(record["title"])
        touched = False
        for turn in record["transcript"]:
            inferred = guest if guest and turn.get("style") == "answer" else None
            if turn.get("inferred_speaker") != inferred:
                if inferred is None:
                    turn.pop("inferred_speaker", None)
                else:
                    turn["inferred_speaker"] = inferred
                touched = True
            if inferred:
                enriched_turns += 1
        if touched:
            path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
            entry["enriched_at"] = manifest.now_iso()
            enriched_eps += 1
    manifest.save(m)
    print(f"enrich: {enriched_turns} answer turns attributed across {enriched_eps} updated episodes")
