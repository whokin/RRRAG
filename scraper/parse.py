"""parse: Page Snapshots -> Episode Records (data/raw/), freely re-runnable.

Written against the probe episodes (#50, #150, #250, #350, #416). Era quirks
the probe surfaced:
  - "Read the Transcript:" casing varies; #50-era key points live in a <ul>
    whose items are duplicated as sibling <p>s
  - speaker labels are <strong> in some eras, plain text in others
  - one Speaker Turn can span multiple <p>s (continuations are unlabeled)
  - key-point timestamps: "[0:01:58.0]" old era, "(0:04:01)" new era
"""

import json
import re

from bs4 import BeautifulSoup

from . import manifest

KEY_POINTS_MARKER = re.compile(r"key points from this episode", re.I)
TRANSCRIPT_MARKER = re.compile(r"read the transcript|^transcript:?\s*$", re.I)
# post-transcript reference sections; all of them carry harvestable links
REFERENCES_MARKER = re.compile(
    r"links from today|books from today|papers from today|participate in our", re.I
)

TIMESTAMP = re.compile(r"[\[(](\d+:\d{2}(?::\d{2})?(?:\.\d)?)[\])]")
# optional leading timestamp, then "Firstname [Middle] Lastname:"
SPEAKER = re.compile(
    r"^(?:[\[(]\d+:\d{2}(?::\d{2})?(?:\.\d+)?[\])]\s*)?"
    r"([A-Z][\w.'’-]*(?:\s+[A-Z][\w.'’-]*){0,3}):\s*(.*)$",
    re.S,
)

# label-shaped prefixes that aren't people (outro boilerplate)
NON_SPEAKER_LABELS = {"Disclaimer", "Note", "Announcement", "Correction"}

MIN_TRANSCRIPT_CHARS = 1000
REQUIRED = ("episode", "title", "date", "transcript_text")


def _blocks(body):
    """Paragraph-level blocks in document order; <p> inside a list is the
    list's content, not a separate block (the #50-era duplication)."""
    return [
        b
        for b in body.find_all(["p", "h2", "h3", "h4", "ul", "ol"])
        if not (b.name == "p" and b.find_parent(["ul", "ol"]))
    ]


def _fully_bold(p) -> bool:
    """The interview-era format (#250): host questions are entirely-bold
    paragraphs with no name label; guest answers are plain paragraphs."""
    strong = p.find("strong")
    return strong is not None and strong.get_text(" ", strip=True) == p.get_text(" ", strip=True)


def _add_links(block, links: list[dict]) -> None:
    for a in block.find_all("a", href=True):
        if a["href"].startswith("/podcast/tag/"):
            continue  # article footer tag, not an episode reference
        anchor_text = a.get_text(" ", strip=True)
        title = anchor_text
        if not title or title.startswith(("http", "www.", "@")):
            container = a.find_parent("li") or a.find_parent("p") or block
            context = container.get_text(" ", strip=True).replace(anchor_text, "").strip(" —–-:.")
            title = context or anchor_text
        link = {"title": title, "url": a["href"]}
        if title and link not in links:
            links.append(link)


# "Title — https://url" plain-text reference (the #350 era publishes links as
# text, not anchors, and long URLs wrap across paragraphs)
DASH_SPLIT = re.compile(r"\s+[—–-]\s+")
URL_LIKE = re.compile(r"(https?://\S+|www\.\S+|[\w.-]+\.[a-z]{2,}/\S*)", re.I)


def _text_ref(text: str, entries: list[list[str]]) -> None:
    parts = DASH_SPLIT.split(text, maxsplit=1)
    if len(parts) == 2 and (
        URL_LIKE.search(parts[1]) or re.fullmatch(r"https?://", parts[1].strip())
    ):
        entries.append([parts[0].strip("'’‘\" "), parts[1]])
    elif entries and not DASH_SPLIT.search(text):
        entries[-1][1] += text  # wrapped-URL continuation line

def _flush_text_refs(entries: list[list[str]], links: list[dict]) -> None:
    for title, url_text in entries:
        url = re.sub(r"\s+", "", url_text).rstrip(".,;")
        if "://" not in url:
            url = "https://" + url
        link = {"title": title, "url": url}
        if title and link not in links:
            links.append(link)


def _key_point(text: str) -> dict | None:
    m = TIMESTAMP.search(text)
    stripped = TIMESTAMP.sub("", text).strip(" .—-")
    if not stripped:
        return None
    return {"timestamp": m.group(1) if m else None, "text": stripped}


def parse_snapshot(html: str, entry: dict) -> tuple[dict | None, list[str], list[str]]:
    """Returns (record, gaps, flags). record is None when required fields fail."""
    soup = BeautifulSoup(html, "lxml")
    body = soup.select_one("article.entry")
    if body is None:
        return None, [], ["no article.entry container — not an episode page?"]

    h1 = body.find("h1") or soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else None

    time_el = body.find("time") or soup.find("time")
    date = time_el.get("datetime") if time_el else None

    episode = entry["episode"]
    if episode is None and title:
        m = re.search(r"episode\s+(\d+)", title, re.I) or re.search(r"#(\d+)\b", title)
        if m:
            episode = int(m.group(1))

    summary_parts: list[str] = []
    key_points: list[dict] = []
    turns: list[dict] = []
    links: list[dict] = []
    section = "summary"
    after_bold_question = False
    text_refs: list[list[str]] = []

    for block in _blocks(body):
        text = block.get_text(" ", strip=True)
        if not text or not re.search(r"\w", text):  # empty or a "***" separator
            continue
        if KEY_POINTS_MARKER.search(text[:60]):
            section = "key_points"
            continue
        if TRANSCRIPT_MARKER.search(text[:60]):
            section = "transcript"
            continue
        # reference sections are always real headers; a transcript sentence
        # merely *mentioning* "links" must not end the transcript
        if block.name in ("h2", "h3", "h4") and REFERENCES_MARKER.search(text[:60]):
            section = "references"
            continue

        if section == "summary":
            summary_parts.append(text)
        elif section == "key_points":
            if block.name in ("ul", "ol"):
                items = [li.get_text(" ", strip=True) for li in block.find_all("li")]
            else:
                items = [text]
            for item in items:
                kp = _key_point(item)
                if kp and kp not in key_points:
                    key_points.append(kp)
        elif section == "transcript":
            if block.name != "p":
                continue
            m = SPEAKER.match(text)
            if m and len(m.group(1)) <= 40 and m.group(1) in NON_SPEAKER_LABELS:
                turns.append({"speaker": None, "text": text})  # boilerplate, not a person
                after_bold_question = False
            elif m and len(m.group(1)) <= 40:
                turns.append({"speaker": m.group(1), "text": m.group(2).strip()})
                after_bold_question = False
            elif _fully_bold(block):
                turns.append({"speaker": None, "text": text})
                after_bold_question = True
            elif after_bold_question:
                turns.append({"speaker": None, "text": text})  # the answer begins
                after_bold_question = False
            elif turns:
                turns[-1]["text"] += "\n\n" + text
            else:
                turns.append({"speaker": None, "text": text})
        elif section == "references":
            if block.find("a", href=True):
                _add_links(block, links)
            else:
                _text_ref(text, text_refs)

    _flush_text_refs(text_refs, links)
    transcript_text = "\n\n".join(t["text"] for t in turns)
    speakers = sorted({t["speaker"] for t in turns if t["speaker"]})
    summary = "\n\n".join(summary_parts) or None

    flags = []
    values = {
        "episode": episode,
        "title": title,
        "date": date,
        "transcript_text": transcript_text if len(transcript_text) >= MIN_TRANSCRIPT_CHARS else None,
    }
    for field in REQUIRED:
        if not values[field]:
            detail = f" ({len(transcript_text)} chars)" if field == "transcript_text" else ""
            flags.append(f"missing required: {field}{detail}")
    if flags:
        return None, [], flags

    gaps = []
    unattributed = sum(1 for t in turns if not t["speaker"])
    if not speakers:
        gaps.append("no speaker labels")
    elif unattributed:
        gaps.append(f"unattributed turns: {unattributed}/{len(turns)}")
    if not summary:
        gaps.append("no summary")
    if not key_points:
        gaps.append("no key points")
    if not links:
        gaps.append("no links")

    record = {
        "episode": episode,
        "title": title,
        "date": date,
        "speakers": speakers,
        "summary": summary,
        "key_points": key_points,
        "transcript": turns,
        "links": links,
        "source_url": entry["url"],
    }
    return record, gaps, flags


def run(episodes: list[int] | None = None, reparse_all: bool = False) -> None:
    m = manifest.load()
    statuses = ("fetched", "parsed", "flagged") if (reparse_all or episodes) else ("fetched",)
    targets = manifest.select(m, episodes=episodes, statuses=statuses)
    targets = [e for e in targets if e["fetched_at"]]
    if not targets:
        print("parse: nothing to parse")
        return

    manifest.RAW_DIR.mkdir(parents=True, exist_ok=True)
    parsed = flagged = 0
    for entry in targets:
        html_path = manifest.HTML_DIR / f"{entry['slug']}.html"
        record, gaps, flags = parse_snapshot(html_path.read_text(), entry)
        entry["flags"] = flags
        entry["gaps"] = gaps
        entry["parsed_at"] = manifest.now_iso()
        if record is None:
            entry["status"] = "flagged"
            flagged += 1
            print(f"parse: FLAGGED {entry['slug']} — {'; '.join(flags)}")
        else:
            entry["episode"] = record["episode"]
            entry["status"] = "parsed"
            out = manifest.RAW_DIR / f"{entry['slug']}.json"
            out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
            parsed += 1
            note = f" (gaps: {', '.join(gaps)})" if gaps else ""
            print(
                f"parse: {entry['slug']} — ep {record['episode']}, "
                f"{len(record['transcript'])} turns, {len(record['speakers'])} speakers, "
                f"{len(record['key_points'])} key points, {len(record['links'])} links{note}"
            )
    _dedupe_aliases(m)
    manifest.save(m)
    print(f"parse: {parsed} Episode Records, {flagged} flagged")


def _slug_rank(entry: dict) -> tuple:
    """Canonical preference: pure-numeric slug, then any slug with digits,
    then alphabetical. The show publishes topic/guest alias URLs for the
    same post; content is byte-identical."""
    slug = entry["slug"]
    return (not slug.isdigit(), not any(c.isdigit() for c in slug), slug)


def _dedupe_aliases(m: dict[str, dict]) -> None:
    by_episode: dict[int, list[dict]] = {}
    for entry in m.values():
        if entry["status"] == "parsed" and entry["episode"] is not None:
            by_episode.setdefault(entry["episode"], []).append(entry)
    demoted = 0
    for group in by_episode.values():
        if len(group) < 2:
            continue
        group.sort(key=_slug_rank)
        canonical, *aliases = group
        for entry in aliases:
            entry["status"] = "alias"
            entry["alias_of"] = canonical["slug"]
            (manifest.RAW_DIR / f"{entry['slug']}.json").unlink(missing_ok=True)
            demoted += 1
    if demoted:
        print(f"parse: {demoted} alias URLs demoted (duplicate episode content)")
