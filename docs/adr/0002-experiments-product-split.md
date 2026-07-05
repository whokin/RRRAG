# Learning happens in a sandbox; the product only receives promoted techniques

The roadmap's value depends on A/B-comparing techniques (does hybrid beat naive
*on this corpus*?), which is impossible if only one current version exists in
the product. Experiments live in `experiments/` (notebooks, every Stage kept
runnable); a technique is Promoted into the product only after winning on the
Golden Set. Rejected alternatives: one evolving codebase where git history is
the roadmap (loses side-by-side comparison), and a throwaway sandbox rebuilt
from scratch afterward (duplicates work without adding learning).
