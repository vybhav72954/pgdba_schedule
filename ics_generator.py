"""Generate a valid RFC 5545 .ics string for a list of sessions.

No external icalendar library — we emit the text by hand to keep the dependency
surface minimal. CRLF line endings are required by RFC 5545.
"""

from __future__ import annotations

import datetime
import hashlib

from scheduler import COURSE_NAMES, INSTRUCTORS

CRLF = "\r\n"
TZID = "Asia/Kolkata"
PRODID = "-//PGDBA Schedule App//IIM Calcutta Batch-11//EN"


def _escape(text: str) -> str:
    # RFC 5545 §3.3.11 — escape backslash, semicolon, comma, and newlines.
    return (
        text.replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n")
            .replace("\r", "")
    )


def _fmt_local(date: datetime.date, hhmm: str) -> str:
    h, m = hhmm.split(":")
    return f"{date.strftime('%Y%m%d')}T{int(h):02d}{int(m):02d}00"


def _uid(session: dict) -> str:
    # Audit events get a distinct UID so they don't collide with a
    # hypothetical non-audit export of the same course; core/elective UIDs
    # stay stable across re-exports (Google Calendar then updates rather than
    # duplicating on re-import).
    audit_marker = "AUDIT|" if session.get("category") == "audit" else ""
    raw = f"{audit_marker}{session['date']}|{session['start']}|{session['session']}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]
    return f"{digest}@pgdba-schedule.local"


def _vtimezone() -> list[str]:
    # Static IST definition. India does not observe DST, so a single STANDARD
    # block with TZOFFSETFROM == TZOFFSETTO is sufficient.
    return [
        "BEGIN:VTIMEZONE",
        f"TZID:{TZID}",
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0530",
        "TZOFFSETTO:+0530",
        "TZNAME:IST",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]


def _vevent(session: dict, dtstamp: str) -> list[str]:
    course = session["course"]
    full_name = COURSE_NAMES.get(course, course)
    instructor = INSTRUCTORS.get(course, "")
    is_audit = session.get("category") == "audit"
    prefix = "[AUDIT] " if is_audit else ""
    summary = f"{prefix}{session['session'].split(':')[0].strip()} | {full_name}"
    description = "Auditing — " + instructor if is_audit and instructor else instructor

    lines = [
        "BEGIN:VEVENT",
        f"UID:{_uid(session)}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;TZID={TZID}:{_fmt_local(session['date'], session['start'])}",
        f"DTEND;TZID={TZID}:{_fmt_local(session['date'], session['end'])}",
        f"SUMMARY:{_escape(summary)}",
        f"DESCRIPTION:{_escape(description)}",
        f"LOCATION:{_escape('IIM Calcutta')}",
    ]
    if is_audit:
        lines.append("CATEGORIES:AUDIT")
    lines += [
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder",
        "TRIGGER:-PT15M",
        "END:VALARM",
        "END:VEVENT",
    ]
    return lines


def generate_ics(sessions: list[dict]) -> str:
    dtstamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODID}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:PGDBA Sem-III Schedule",
        f"X-WR-TIMEZONE:{TZID}",
    ]
    lines += _vtimezone()
    for session in sessions:
        lines += _vevent(session, dtstamp)
    lines.append("END:VCALENDAR")
    return CRLF.join(lines) + CRLF
