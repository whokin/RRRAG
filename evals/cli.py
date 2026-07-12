"""CLI: evals retrieval [--label naive] [-k 8]."""

import argparse


def main() -> None:
    ap = argparse.ArgumentParser(prog="evals")
    sub = ap.add_subparsers(dest="command", required=True)

    p_ret = sub.add_parser("retrieval", help="hit-rate@k + MRR against the Golden Set")
    p_ret.add_argument("--label", default="naive", help="run label for evals/runs/<date>-<label>.json")
    p_ret.add_argument("-k", type=int, default=8)
    p_ret.add_argument("--no-save", action="store_true")

    p_sp = sub.add_parser("synth-prompts", help="sample chunks, write generation prompts")
    p_sp.add_argument("--n", type=int, default=35)
    p_sp.add_argument("--seed", type=int, default=42)
    sub.add_parser("synth-collect", help="validate generated questions into golden.jsonl")

    args = ap.parse_args()

    if args.command == "synth-prompts":
        from . import synthesize

        synthesize.make_prompts(n=args.n, seed=args.seed)
    elif args.command == "synth-collect":
        from . import synthesize

        synthesize.collect()
    elif args.command == "retrieval":
        from . import retrieval

        result = retrieval.evaluate(k=args.k)

        def show(name: str, m: dict) -> None:
            hits = "  ".join(f"{key}={val}" for key, val in m.items() if key.startswith("hit"))
            print(f"{name:12s} n={m['n']:<3d} {hits}  mrr={m['mrr']}")

        show("overall", result["overall"])
        for prov, m in result["by_provenance"].items():
            show(f"  {prov}", m)
        misses = [i["id"] for i in result["per_question"] if not i["rank"]]
        if misses:
            print(f"complete misses (no pinned episode in top {result['k']}): {', '.join(misses)}")
        if not args.no_save:
            from .retrieval import save_run

            path = save_run(result, args.label)
            print(f"saved {path}")


if __name__ == "__main__":
    main()
