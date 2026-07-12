#!/usr/bin/env python3
"""Predict-before-reveal gate (CLAUDE.md learning protocol, rule 2).

PreToolUse hook on Bash: blocks eval/measurement runs unless PLAN.md's
"Learning protocol ledger" holds an open prediction line. Being blocked
here is the protocol working, not an error — record the user's prediction
in the ledger, then re-run.
"""
import json
import os
import re
import sys

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")

# Measurement invocations only (incl. docker-wrapped): a runner in front of
# an evals subcommand. Merely mentioning the command (grep, echo) can still
# trip this if the full invocation string appears — cost of a false block is
# one re-run, so stay simple rather than parse shell.
if not re.search(
    r"(uv\s+run|python3?\s+-m)\s+evals\s+(retrieval|generation|judge|run)\b", cmd
):
    sys.exit(0)

# --no-save runs are schema/loading validation (session brief 02 pattern),
# not measurements — allowed, but discard stdout to keep numbers unspoiled.
if "--no-save" in cmd:
    sys.exit(0)

root = os.environ.get("CLAUDE_PROJECT_DIR", ".")
try:
    with open(os.path.join(root, "PLAN.md")) as f:
        plan = f.read()
except OSError:
    sys.exit(0)  # no PLAN.md (odd cwd?) — don't wedge the session

if re.search(r"^- PREDICTION", plan, re.MULTILINE):
    sys.exit(0)  # prediction on record — run away

print(
    "Learning protocol (predict-before-reveal): no open '- PREDICTION' line "
    "in PLAN.md's Learning protocol ledger. Before this eval runs, ask the "
    "user for a written prediction (a number plus a confidence level), "
    "record it in the ledger, then re-run this command.",
    file=sys.stderr,
)
sys.exit(2)
