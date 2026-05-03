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


def _validate_electives(values: list[str]) -> tuple[list[str], str | None]:
    cleaned = [v.strip() for v in values if v and v.strip()]
    cleaned = list(dict.fromkeys(cleaned))  # de-dup, preserve order
    if len(cleaned) != 4:
        return cleaned, "Please select exactly 4 electives."
    unknown = [c for c in cleaned if c not in ALL_ELECTIVES]
    if unknown:
        return cleaned, f"Unknown elective code(s): {', '.join(unknown)}."
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

    @app.route("/schedule", methods=["POST"])
    def schedule_view():
        selected = request.form.getlist("electives")
        cleaned, error = _validate_electives(selected)
        if error:
            return render_template(
                "index.html",
                view="select",
                electives=elective_options,
                core_courses=CORE_COURSES,
                course_names=COURSE_NAMES,
                instructors=INSTRUCTORS,
                error=error,
                preselected=cleaned,
            ), 400

        sessions = get_schedule(app.config["MASTER_SESSIONS"], cleaned)
        weeks = _group_by_week(sessions)
        return render_template(
            "index.html",
            view="schedule",
            electives=elective_options,
            selected=cleaned,
            weeks=weeks,
            session_count=len(sessions),
            ibc_selected=("IBC" in cleaned),
            core_courses=CORE_COURSES,
            course_names=COURSE_NAMES,
            instructors=INSTRUCTORS,
        )

    @app.route("/export", methods=["POST"])
    def export_ics():
        selected = request.form.getlist("electives")
        cleaned, error = _validate_electives(selected)
        if error:
            return render_template(
                "index.html",
                view="select",
                electives=elective_options,
                core_courses=CORE_COURSES,
                course_names=COURSE_NAMES,
                instructors=INSTRUCTORS,
                error=error,
                preselected=cleaned,
            ), 400

        sessions = get_schedule(app.config["MASTER_SESSIONS"], cleaned)
        ics_text = generate_ics(sessions)
        response = make_response(ics_text)
        response.headers["Content-Type"] = "text/calendar; charset=utf-8"
        response.headers["Content-Disposition"] = (
            'attachment; filename="PGDBA_Sem3_Schedule.ics"'
        )
        return response

    return app
