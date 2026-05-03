# PGDBA Batch-11 — Semester III Schedule App

A locally-run Flask web app for PGDBA Batch-11 students at IIM Calcutta. Pick your 4 electives, view your full personalised timetable (core + electives), and export it as an `.ics` file for Google Calendar / Apple Calendar / Outlook.

Runs on `localhost`. No login, no hosting, no API keys.

## Setup

**Step 1 — Install uv** (skip if already installed)

**Step 2 — Clone the repository**

    git clone https://github.com/vybhav72954/pgdba_schedule.git
    cd pgdba_schedule

**Step 3 — Create a virtual environment**

    uv venv

**Step 4 — Install dependencies**

    uv pip install -r requirements.txt

**Step 5 — Run the app**

    uv run python main.py

**Step 6 — Open in your browser**

    http://localhost:5000

## Usage

Select your 4 electives → view your schedule → click **Export to Calendar (.ics)** to download the file → double-click the file to import into Google Calendar, Apple Calendar, or Outlook. Each event includes a 15-minute reminder.

## Notes

- IBC sessions are not yet in the master schedule and will not appear in your timetable even if selected. The app surfaces a small note when this happens.
