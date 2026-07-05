"""CLI entry point. Subcommands mirror the pipeline (PLAN.md):

  discover  sitemap.xml -> Manifest
  fetch     Manifest -> Page Snapshots (bronze)
  parse     Page Snapshots -> Episode Records (silver)
  refresh   discover + fetch + parse, new episodes only
  status    Manifest summary
"""

import argparse
from collections import Counter


def _episodes_arg(value: str) -> list[int]:
    return [int(x) for x in value.split(",") if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(prog="scraper")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("discover", help="read sitemap.xml, seed the Manifest")

    p_fetch = sub.add_parser("fetch", help="fetch Page Snapshots for discovered episodes")
    p_fetch.add_argument("--episodes", type=_episodes_arg, help="comma-separated episode numbers")
    p_fetch.add_argument("--limit", type=int)
    p_fetch.add_argument("--force", action="store_true", help="deliberate correction re-fetch")

    p_parse = sub.add_parser("parse", help="derive Episode Records from Page Snapshots")
    p_parse.add_argument("--episodes", type=_episodes_arg)
    p_parse.add_argument("--all", action="store_true", help="re-parse everything, not just fetched")

    sub.add_parser("refresh", help="discover + fetch + parse anything new")
    sub.add_parser("status", help="Manifest summary")

    args = ap.parse_args()

    if args.command == "discover":
        from . import discover

        discover.run()
    elif args.command == "fetch":
        from . import fetch

        fetch.run(episodes=args.episodes, limit=args.limit, force=args.force)
    elif args.command == "parse":
        from . import parse

        parse.run(episodes=args.episodes, reparse_all=args.all)
    elif args.command == "refresh":
        from . import discover, fetch, parse

        discover.run()
        fetch.run()
        parse.run()
    elif args.command == "status":
        from . import manifest

        m = manifest.load()
        counts = Counter(e["status"] for e in m.values())
        print(f"{len(m)} episodes in Manifest: " + ", ".join(f"{s}={n}" for s, n in sorted(counts.items())))
        gaps = Counter(g for e in m.values() for g in e["gaps"])
        if gaps:
            print("gaps: " + ", ".join(f"{g}={n}" for g, n in sorted(gaps.items())))
        for e in manifest.select(m, statuses=("flagged",)):
            print(f"  flagged: {e['slug']} — {'; '.join(e['flags'])}")


if __name__ == "__main__":
    main()
