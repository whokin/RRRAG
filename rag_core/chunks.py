"""Episode Records -> Chunks (the gold layer's text units).

Stage 1 is deliberately naive: fixed-size character windows over the
transcript, speaker names inlined as they'd appear on the page. Chunk size
3200 chars ~= 800 tokens (chars/4), 15% overlap. Turn-aware chunking is
Stage 6's variable — don't improve this before the eval exists (PLAN.md).
"""

import json
from pathlib import Path

from scraper import manifest
from scraper.speakers import canonicalize

CHUNK_CHARS = 3200
OVERLAP_CHARS = 480


def episode_text(record: dict) -> str:
    """Transcript as one string, with the effective speaker (observed
    canonical, else inferred guest) prefixed the way the page shows it."""
    lines = []
    for turn in record["transcript"]:
        speaker = canonicalize(turn["speaker"]) or turn.get("inferred_speaker")
        lines.append(f"{speaker}: {turn['text']}" if speaker else turn["text"])
    return "\n\n".join(lines)


def split_text(text: str) -> list[tuple[int, str]]:
    """Fixed windows with overlap; cut at the last whitespace before the
    boundary so words stay whole. Returns (start_offset, chunk_text)."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_CHARS, len(text))
        if end < len(text):
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        chunks.append((start, text[start:end].strip()))
        if end >= len(text):
            break
        start = max(end - OVERLAP_CHARS, start + 1)
    return chunks


def build_chunks(record: dict, slug: str) -> list[dict]:
    text = episode_text(record)
    speakers = sorted(
        {canonicalize(t["speaker"]) for t in record["transcript"] if canonicalize(t["speaker"])}
        | {t["inferred_speaker"] for t in record["transcript"] if t.get("inferred_speaker")}
    )
    return [
        {
            "chunk_id": f"{slug}:{i}",
            "slug": slug,
            "series": record["series"],
            "episode": record["episode"],
            "title": record["title"],
            "date": record["date"],
            "chunk_index": i,
            "char_start": start,
            "speakers": speakers,
            "text": chunk_text,
        }
        for i, (start, chunk_text) in enumerate(split_text(text))
        if chunk_text
    ]


def corpus_chunks(limit: int | None = None) -> list[dict]:
    """All Chunks for every parsed Episode Record."""
    m = manifest.load()
    chunks = []
    for entry in manifest.select(m, statuses=("parsed",)):
        record = json.loads((manifest.RAW_DIR / f"{entry['slug']}.json").read_text())
        chunks.extend(build_chunks(record, entry["slug"]))
        if limit and len(chunks) >= limit:
            return chunks[:limit]
    return chunks


if __name__ == "__main__":
    cs = corpus_chunks()
    total = sum(len(c["text"]) for c in cs)
    print(f"{len(cs)} chunks, {total / 4 / 1e6:.1f}M tokens (est), "
          f"median {sorted(len(c['text']) for c in cs)[len(cs) // 2]} chars/chunk")
