"""Schedule parsing and loading.

Two entry points:

- ``parse_schedule(xlsx_path)`` — reads the master Excel and returns the flat
  session list. Used by the one-shot build script (``build_schedule.py``) and
  not by the running app.
- ``load_schedule(json_path)`` — reads the pre-parsed ``schedule.json`` that
  ships with the app. The Flask app uses this exclusively, so end users never
  need pandas/openpyxl in the request path and never need the Excel file
  present at runtime.
"""

from __future__ import annotations

import datetime
import json
import re
from typing import Any

SHEET_NAME = "Schedule"
DATE_COL = 1

TIME_SLOTS: dict[int, tuple[str, str]] = {
    2: ("08:30", "10:00"),
    3: ("10:15", "11:45"),
    4: ("12:00", "13:30"),
    6: ("14:30", "16:00"),
    7: ("16:15", "17:45"),
}

# Order does not matter for re.match (it anchors at start), but listing the
# longer codes first is harmless and slightly more defensive.
KNOWN_CODES: list[str] = [
    "SAAPM", "EMABE", "CSLBA",
    "CDA", "BDM", "HRM", "CRF", "PRO", "IBC", "FRM", "CMF",
    "PM", "SM", "BE",
]


def _coerce_date(value: Any) -> datetime.date | None:
    # Imported lazily so the running app does not pull in pandas.
    import pandas as pd

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime().date()
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return None


def _detect_course(cell: str) -> str | None:
    text = cell.strip()
    if not text:
        return None
    for code in KNOWN_CODES:
        if re.match(rf"^{code}[\-\s]", text):
            return code
    return None


def parse_schedule(filepath: str) -> list[dict]:
    """Parse the master Excel into session dicts. Build-time use only."""
    import pandas as pd

    df = pd.read_excel(filepath, sheet_name=SHEET_NAME, header=None)

    sessions: list[dict] = []
    for _, row in df.iterrows():
        date = _coerce_date(row[DATE_COL])
        if date is None:
            continue

        for col, (start, end) in TIME_SLOTS.items():
            if col >= len(row):
                continue
            cell = row[col]
            if not isinstance(cell, str):
                continue
            course = _detect_course(cell)
            if course is None:
                continue
            sessions.append({
                "date": date,
                "day": date.strftime("%A"),
                "start": start,
                "end": end,
                "course": course,
                "session": cell.strip(),
            })

    sessions.sort(key=lambda s: (s["date"], s["start"]))
    return sessions


def serialise_sessions(sessions: list[dict]) -> list[dict]:
    """Convert ``date`` objects to ISO strings so the list is JSON-safe."""
    return [
        {**s, "date": s["date"].isoformat()}
        for s in sessions
    ]


def load_schedule(json_path: str) -> list[dict]:
    """Load the pre-parsed schedule shipped with the app."""
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    sessions: list[dict] = []
    for s in raw:
        sessions.append({
            **s,
            "date": datetime.date.fromisoformat(s["date"]),
        })
    sessions.sort(key=lambda s: (s["date"], s["start"]))
    return sessions
