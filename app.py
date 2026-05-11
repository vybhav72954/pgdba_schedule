"""Flask app factory and routes."""

from __future__ import annotations

from collections import defaultdict

from flask import Flask, make_response, render_template, request

from ics_generator import generate_ics
from parser import load_schedule
from scheduler import (
    ALL_ELECTIVES,
    COURSE_NAMES,
    CORE_COURSES,
    INSTRUCTORS,
    get_schedule,
)

SCHEDULE_JSON = "schedule.json"


MAX_AUDITS = 3


def _validate_electives(values: list[str]) -> tuple[list[str], str | None]:
    cleaned = [v.strip() for v in values if v and v.strip()]
    cleaned = list(dict.fromkeys(cleaned))  # de-dup, preserve order
    if len(cleaned) != 4:
        return cleaned, "Please select exactly 4 electives."
    unknown = [c for c in cleaned if c not in ALL_ELECTIVES]
    if unknown:
        return cleaned, f"Unknown elective code(s): {', '.join(unknown)}."
    return cleaned, None


def _validate_audits(
    values: list[str], chosen_electives: list[str]
) -> tuple[list[str], str | None]:
    cleaned = [v.strip() for v in values if v and v.strip()]
    cleaned = list(dict.fromkeys(cleaned))
    if not cleaned:
        return [], None
    unknown = [c for c in cleaned if c not in ALL_ELECTIVES]
    if unknown:
        return cleaned, f"Unknown audit code(s): {', '.join(unknown)}."
    overlap = [c for c in cleaned if c in chosen_electives]
    if overlap:
        return cleaned, (
            f"Cannot audit a course you've already selected as an elective: "
            f"{', '.join(overlap)}."
        )
    if len(cleaned) > MAX_AUDITS:
        return cleaned, f"Pick at most {MAX_AUDITS} courses to audit."
    return cleaned, None


def _iso_week(date) -> tuple[int, int]:
    iso = date.isocalendar()
    return (iso[0], iso[1])


def _group_by_week(sessions: list[dict]) -> list[dict]:
    """Return [{week_label, sessions: [...]}, ...] grouped by ISO week."""
    grouped: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for s in sessions:
        grouped[_iso_week(s["date"])].append(s)
    weeks: list[dict] = []
    for key in sorted(grouped):
        rows = grouped[key]
        first = rows[0]["date"]
        last = rows[-1]["date"]
        label = (
            f"Week of {first.strftime('%d %b')} – {last.strftime('%d %b %Y')}"
            if first != last
            else f"Week of {first.strftime('%d %b %Y')}"
        )
        weeks.append({"label": label, "sessions": rows})
    return weeks


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MASTER_SESSIONS"] = load_schedule(SCHEDULE_JSON)

    elective_options = [
        {"code": code, "name": COURSE_NAMES[code]} for code in ALL_ELECTIVES
    ]

    @app.route("/", methods=["GET"])
    def index():
        return render_template(
            "index.html",
            view="select",
            electives=elective_options,
            core_courses=CORE_COURSES,
            course_names=COURSE_NAMES,
            instructors=INSTRUCTORS,
        )

    def _render_select_error(error: str, preselected_electives, preselected_audits):
        return render_template(
            "index.html",
            view="select",
            electives=elective_options,
            core_courses=CORE_COURSES,
            course_names=COURSE_NAMES,
            instructors=INSTRUCTORS,
            error=error,
            preselected=preselected_electives,
            preselected_audits=preselected_audits,
        ), 400

    def _parse_request():
        elective_input = request.form.getlist("electives")
        audit_input = request.form.getlist("audits")
        electives, e_err = _validate_electives(elective_input)
        if e_err:
            return None, None, _render_select_error(e_err, electives, audit_input)
        audits, a_err = _validate_audits(audit_input, electives)
        if a_err:
            return None, None, _render_select_error(a_err, electives, audits)
        return electives, audits, None

    def _ics_response(ics_text: str, filename: str):
        response = make_response(ics_text)
        response.headers["Content-Type"] = "text/calendar; charset=utf-8"
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @app.route("/schedule", methods=["POST"])
    def schedule_view():
        electives, audits, err_response = _parse_request()
        if err_response is not None:
            return err_response

        sessions = get_schedule(app.config["MASTER_SESSIONS"], electives, audits)
        weeks = _group_by_week(sessions)
        audit_count = sum(1 for s in sessions if s.get("category") == "audit")
        return render_template(
            "index.html",
            view="schedule",
            electives=elective_options,
            selected=electives,
            audits=audits,
            weeks=weeks,
            session_count=len(sessions),
            audit_session_count=audit_count,
            ibc_selected=("IBC" in electives),
            core_courses=CORE_COURSES,
            course_names=COURSE_NAMES,
            instructors=INSTRUCTORS,
        )

    @app.route("/export", methods=["POST"])
    def export_ics():
        electives, audits, err_response = _parse_request()
        if err_response is not None:
            return err_response

        sessions = get_schedule(app.config["MASTER_SESSIONS"], electives, audits)
        schedule_only = [s for s in sessions if s["category"] != "audit"]
        return _ics_response(generate_ics(schedule_only), "PGDBA_Sem3_Schedule.ics")

    @app.route("/export-audit", methods=["POST"])
    def export_audit_ics():
        electives, audits, err_response = _parse_request()
        if err_response is not None:
            return err_response
        if not audits:
            return _render_select_error(
                "No audited courses selected.", electives, audits
            )

        sessions = get_schedule(app.config["MASTER_SESSIONS"], electives, audits)
        audit_only = [s for s in sessions if s["category"] == "audit"]
        return _ics_response(generate_ics(audit_only), "PGDBA_Sem3_Audits.ics")

    return app
