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

Select your 4 electives → view your schedule → click **Export to Calendar (.ics)** to download the file → import it into Google Calendar, Apple Calendar, or Outlook. Each event includes a 15-minute reminder.

## Recommended: import into a dedicated Google Calendar

By default, Google Calendar dumps an imported `.ics` into your **primary** calendar, mixed in with everything else. The cleaner setup is to drop the schedule into its own calendar — then you can toggle it on/off from the sidebar checkbox, change its colour, and (worst case) delete the whole calendar in one click.

1. Open [Google Calendar](https://calendar.google.com) on a desktop browser.
2. In the left sidebar, hover **Other calendars** → click **+** → **Create new calendar**.
3. Name it something like `PGDBA Sem-III` and click **Create calendar**.
4. Open **Settings** (gear icon, top-right) → **Import & export** → **Import**.
5. Pick the `.ics` file you downloaded from this app.
6. Under **Add to calendar**, choose the `PGDBA Sem-III` calendar you just created (not your primary).
7. Click **Import**.

The schedule now lives in its own calendar — toggle it via the sidebar checkbox.

## Accidentally imported? Remove the events

If you imported into your primary calendar by mistake, or want a clean slate, run the Google Apps Script in [`tools/cleanup.gs`](tools/cleanup.gs). It only deletes events created by this app (matched by a unique UID marker) — everything else stays put. No API keys, no Cloud project setup.

1. Open [script.google.com](https://script.google.com) signed in to the Gmail account you want to clean.
2. Click **New project**, replace the default code with the contents of [`tools/cleanup.gs`](tools/cleanup.gs).
3. In the function dropdown at the top, pick **`listPGDBAEvents`** and click **Run**.
4. Approve the Google Calendar permission prompt.
5. Open **Execution log** (bottom panel) — it shows how many events would be removed, per calendar. Nothing is deleted yet.
6. If the count looks right, switch the dropdown to **`removePGDBAEvents`** and click **Run** again. Done.

To clean another Gmail account, sign in to that account at script.google.com and repeat. (If you used the dedicated-calendar approach above, you can also just delete the `PGDBA Sem-III` calendar from Google Calendar settings — even simpler.)

## Notes

- IBC sessions are not yet in the master schedule and will not appear in your timetable even if selected. The app surfaces a small note when this happens.

## Rebuilding `schedule.json`

In future onve we get IBC schedule, we will have to update the `schedule.json`.

1. Drop the new Excel into `data/` keeping the original filename (`PGDBA_Batch-11_Semester-III_Class_Schedule_24-04-2026.xlsx`), or pass `--input` to the script.
2. Run:

       uv run python build_schedule.py

3. Commit the updated `schedule.json`.
