"""Retrieve -> stuff prompt -> Claude answer. The naive baseline every later
Stage is measured against; resist improving it before Stage 2's eval exists."""

import anthropic

from . import index

MODEL = "claude-opus-4-8"

SYSTEM = """\
You answer questions about the Rational Reminder podcast (a Canadian podcast \
on sensible investing hosted by Benjamin Felix and colleagues) using ONLY the \
transcript excerpts provided. Rules:
- Cite the episode after each claim, e.g. [Episode 250] or [Crypto 5].
- If the excerpts don't contain enough to answer, say so plainly — never \
fill gaps from outside knowledge.
- Attribute views to named speakers only when the excerpt shows that person \
saying it; interview answers marked with the guest's name are the guest's \
views, not the hosts'."""


def _label(row: dict) -> str:
    series = "Crypto " if row["series"] == "crypto" else "Episode "
    return f"{series}{row['episode']}"


def ask(question: str, k: int = 8) -> dict:
    rows = index.search(question, k=k)
    excerpts = "\n\n".join(
        f"--- Excerpt {i + 1}: {_label(r)} — \"{r['title']}\" ({r['date']}) ---\n{r['text']}"
        for i, r in enumerate(rows)
    )
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"{excerpts}\n\nQuestion: {question}",
            }
        ],
    )
    if response.stop_reason == "refusal":
        answer = "(The model declined to answer this request.)"
    else:
        answer = "".join(b.text for b in response.content if b.type == "text")
    return {
        "answer": answer,
        "sources": [
            {
                "label": _label(r),
                "title": r["title"],
                "slug": r["slug"],
                "chunk_id": r["chunk_id"],
                "distance": round(r["_distance"], 4),
            }
            for r in rows
        ],
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }
