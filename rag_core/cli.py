"""CLI: rag index | rag search "q" | rag ask "q"."""

import argparse


def main() -> None:
    ap = argparse.ArgumentParser(prog="rag")
    sub = ap.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="chunk + embed the corpus into LanceDB")
    p_index.add_argument("--limit", type=int, help="only index the first N chunks (smoke test)")
    p_index.add_argument("--rebuild", action="store_true", help="drop the table and start fresh")

    p_search = sub.add_parser("search", help="retrieval only — no LLM call")
    p_search.add_argument("query")
    p_search.add_argument("-k", type=int, default=8)

    p_ask = sub.add_parser("ask", help="retrieve + generate an answer")
    p_ask.add_argument("question")
    p_ask.add_argument("-k", type=int, default=8)

    args = ap.parse_args()

    if args.command == "index":
        from . import index

        index.build(limit=args.limit, rebuild=args.rebuild)
    elif args.command == "search":
        from . import index

        for r in index.search(args.query, k=args.k):
            head = r["text"][:140].replace("\n", " ")
            print(f"{r['_distance']:.4f}  {r['series']} {r['episode']:>3} #{r['chunk_index']:<3} {head}")
    elif args.command == "ask":
        from . import answer

        result = answer.ask(args.question, k=args.k)
        print(result["answer"])
        print("\nSources:")
        for s in result["sources"]:
            print(f"  {s['distance']:.4f}  {s['label']} — {s['title'][:60]}")
        print(f"\n({result['usage']['input_tokens']} in / {result['usage']['output_tokens']} out tokens)")


if __name__ == "__main__":
    main()
