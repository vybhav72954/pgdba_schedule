/**
 * PGDBA Schedule — Google Calendar cleanup
 *
 * Removes events created by the PGDBA Schedule App from the signed-in Google
 * account. Safe to re-run; matches only events with the app's UID marker or
 * (as a fallback) location "IIM Calcutta" + a known course-code title.
 *
 * How to use
 *   1. Open https://script.google.com and click "New project".
 *   2. Paste this entire file into Code.gs (replace the default content).
 *   3. Save the Project with a Name and save it to Drive
 *   4. From the function dropdown at the top, pick `listPGDBAEvents`, click
 *      Run, and approve the Google Calendar permission prompt.
 *   5. Click "Execution log" at the bottom and check the count + per-calendar
 *      breakdown. Nothing has been deleted yet — this is a dry run.
 *   6. If the list looks right, switch the dropdown to `removePGDBAEvents`
 *      and click Run. Watch the log for the deletion count.
 *   7. To clean up another Gmail account, sign out of script.google.com,
 *      sign in to the other account, and repeat steps 1–5.
 *
 * What it matches
 *   - Primary signal: the original iCalUID ends with "@pgdba-schedule.local"
 *     (the marker baked into every event by ics_generator.py).
 *   - Fallback signal: LOCATION is exactly "IIM Calcutta" AND the SUMMARY
 *     starts with one of the 14 PGDBA course codes followed by "-" or " ".
 *
 * Scope
 *   Scans every calendar the account has access to (primary + secondary +
 *   subscribed-and-writable), within SCAN_START..SCAN_END. Adjust those if
 *   the schedule range ever extends beyond Semester III.
 */

const UID_MARKER = 'pgdba-schedule.local';
const LOCATION_TAG = 'IIM Calcutta';
const COURSE_CODES = [
  'SAAPM', 'EMABE', 'CSLBA',  // longest codes first so prefix checks are unambiguous
  'CDA', 'BDM', 'HRM', 'CRF', 'PRO', 'IBC', 'FRM', 'CMF',
  'PM', 'SM', 'BE',
];

// Generous window covering all of Semester III. Adjust if needed.
const SCAN_START = new Date('2026-01-01T00:00:00');
const SCAN_END   = new Date('2027-06-30T23:59:59');


/** Dry-run preview — logs what WOULD be deleted. Does not delete anything. */
function listPGDBAEvents() {
  scan_(false);
}

/** Actually deletes the matched events. Run `listPGDBAEvents` first to preview. */
function removePGDBAEvents() {
  scan_(true);
}


function scan_(doDelete) {
  const calendars = CalendarApp.getAllCalendars();
  let total = 0;
  const perCalendar = [];

  for (let i = 0; i < calendars.length; i++) {
    const cal = calendars[i];
    let inCal = 0;
    let events;
    try {
      events = cal.getEvents(SCAN_START, SCAN_END);
    } catch (err) {
      Logger.log('Skipped "' + cal.getName() + '" (cannot read): ' + err);
      continue;
    }

    for (let j = 0; j < events.length; j++) {
      const e = events[j];
      if (!isPGDBAEvent_(e)) continue;
      if (doDelete) {
        try {
          e.deleteEvent();
        } catch (err) {
          Logger.log('Failed to delete "' + e.getTitle() + '" on '
            + e.getStartTime() + ': ' + err);
          continue;
        }
      }
      inCal++;
    }

    if (inCal > 0) {
      perCalendar.push({ name: cal.getName(), count: inCal });
      total += inCal;
    }
  }

  const verb = doDelete ? 'Removed' : '[DRY RUN] Would remove';
  if (total === 0) {
    Logger.log('No PGDBA events found in the scan window. Nothing to do.');
    return;
  }
  Logger.log(verb + ' ' + total + ' event(s) across ' + perCalendar.length + ' calendar(s):');
  for (let k = 0; k < perCalendar.length; k++) {
    Logger.log('  - ' + perCalendar[k].name + ': ' + perCalendar[k].count);
  }
  if (!doDelete) {
    Logger.log('');
    Logger.log('Preview only. To actually delete, run `removePGDBAEvents`.');
  }
}


function isPGDBAEvent_(event) {
  // Primary: original iCalUID preserved on import.
  const id = event.getId();
  if (id && id.indexOf(UID_MARKER) !== -1) return true;

  // Fallback: location + course-code title prefix.
  if (event.getLocation() !== LOCATION_TAG) return false;
  const title = event.getTitle() || '';
  for (let i = 0; i < COURSE_CODES.length; i++) {
    const code = COURSE_CODES[i];
    if (title.indexOf(code + '-') === 0 || title.indexOf(code + ' ') === 0) {
      return true;
    }
  }
  return false;
}
