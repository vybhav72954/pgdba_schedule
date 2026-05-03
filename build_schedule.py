"""One-shot maintainer script: parse the master Excel into ``schedule.json``.

End users never run this — the JSON is committed to the repo and is what the
app reads at runtime. Run this only when the institute publishes a new master
schedule:

    uv run python build_schedule.py

By default it reads
``data/PGDBA_Batch-11_Semester-III_Class_Schedule_24-04-2026.xlsx`` and writes
``schedule.json`` next to the app source. Override either with ``--input`` /
``--output``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from parser import parse_schedule, serialise_sessions

DEFAULT_INPUT = os.path.join(
    "data", "PGDBA_Batch-11_Semester-III_Class_Schedule_24-04-2026.xlsx"
)
DEFAULT_OUTPUT = "schedule.json"


def main() -> int:
    p = argparse.ArgumentParser(description="Rebuild schedule.json from the master Excel.")
    p.add_argument("--input", default=DEFAULT_INPUT, help=f"Path to master Excel (default: {DEFAULT_INPUT})")
    p.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Path to write JSON (default: {DEFAULT_OUTPUT})")
    args = p.parse_args()

    if not os.path.exists(args.input):
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        print("Drop the master Excel into data/ before running this script.", file=sys.stderr)
        return 1

    sessions = parse_schedule(args.input)
    payload = serialise_sessions(sessions)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")

    courses = sorted({s["course"] for s in sessions})
    print(f"Wrote {len(sessions)} sessions across {len(courses)} courses to {args.output}")
    print(f"Courses: {', '.join(courses)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
