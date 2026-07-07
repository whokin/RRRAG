"""Curated speaker-label table (entity resolution, not NER — 298 labels
don't need a model). Built from the 2026-07-06 label inventory; extend as
the Refresh surfaces new variants.

Epistemics: canonicalization is applied downstream (chunking, notebooks) —
the observed `speaker` field in Episode Records always keeps the label
exactly as the page printed it."""

# variant -> canonical display name
CANONICAL = {
    "Benjamin Felix": "Ben Felix",
    "BenFelix": "Ben Felix",
    "BF": "Ben Felix",
    "CP": "Cameron Passmore",
    "McGrath": "Mark McGrath",
}

# label-shaped strings that aren't speakers: book titles read as segment
# headers, section markers. Parser keeps their text but never as a speaker.
JUNK = {
    "Time Smart",
    "The Investment Answer",
    "BONUS",
    "Tagged",
    "Extra",
    "IBD",
    "Range",
    "Essentialism",
    "Grit",
    "Trillions",
    "Video",
    "Text",
}

# the show's hosts across its eras (for analysis; never asserted per-episode
# without in-episode evidence)
KNOWN_HOSTS = {"Ben Felix", "Cameron Passmore", "Dan Bortolotti", "Mark McGrath", "Ben Wilson"}


def canonicalize(name: str | None) -> str | None:
    if name is None or name in JUNK:
        return None
    return CANONICAL.get(name, name)
