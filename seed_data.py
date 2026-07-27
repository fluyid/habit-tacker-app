"""
Generate the 4-week example tracking data (the test fixture).

Run this once to (re)create ``data/habits.json`` with five predefined habits and
four weeks of deliberately imperfect history.
"""

from datetime import date, datetime, timedelta

from backend import HabitManager
from functions import save_habits


# The 4-week window ends here. 2026-03-01 is a Sunday, so the window is exactly
# four whole Monday-to-Sunday weeks: Mon 2026-02-02 .. Sun 2026-03-01.
FIXTURE_END = date(2026, 3, 1)
WINDOW_DAYS = 28


def at(day, hour=9):
    """Turn a date into a datetime at a fixed hour (logs need a full datetime)."""
    return datetime.combine(day, datetime.min.time()).replace(hour=hour)


def all_days():
    """Every date in the window, oldest first (28 dates)."""
    start = FIXTURE_END - timedelta(days=WINDOW_DAYS - 1)
    return [start + timedelta(days=i) for i in range(WINDOW_DAYS)]


def week_mondays():
    """The Monday that starts each of the 4 weeks in the window."""
    start = FIXTURE_END - timedelta(days=WINDOW_DAYS - 1)  # already a Monday
    return [start + timedelta(weeks=w) for w in range(4)]


def seed():
    """Build the manager, log the designed history, and save it to disk."""
    manager = HabitManager()          # starts with the 5 predefined habits
    days = all_days()

    def habit(name):
        return manager.get_habit_by_name(name)

    # Workout (Daily, reps): every day EXCEPT Feb 10-12 (a 3-day gap)
    # Splits the month into an 8-day run and a 17-day run -> longest 17.
    gap = {date(2026, 2, 10), date(2026, 2, 11), date(2026, 2, 12)}
    for day in days:
        if day not in gap:
            habit("Workout").log_progress(value=30, note="", timestamp=at(day))

    # Read a book (Daily, pages): weekdays only, skips every weekend
    # Each Mon-Fri block is a run of 5; the last day (Sun Mar 1) is unlogged.
    for day in days:
        if day.weekday() < 5:  # 0=Mon .. 4=Fri
            habit("Read a book").log_progress(value=20, note="", timestamp=at(day))

    # Meditate (Daily, minutes): sparse first week, then 21 days straight
    # Feb 2, 4, 6 are isolated (streaks of 1); Feb 9 to Mar 1 is unbroken (21).
    sparse = {date(2026, 2, 2), date(2026, 2, 4), date(2026, 2, 6)}
    for day in days:
        if day in sparse or day >= date(2026, 2, 9):
            habit("Meditate").log_progress(value=10, note="", timestamp=at(day))

    # Clean the house (Weekly, Yes/No): completed all 4 weeks
    for monday in week_mondays():
        habit("Clean the house").log_progress(completed=True, note="", timestamp=at(monday))

    # Grocery Shopping (Weekly, Yes/No): weeks 1,2 done, week 3 skipped, 4 done
    mondays = week_mondays()
    for i, monday in enumerate(mondays):
        if i != 2:  # skip the third week
            habit("Grocery Shopping").log_progress(completed=True, note="", timestamp=at(monday))

    save_habits(manager)
    return manager


if __name__ == "__main__":
    manager = seed()
    print(f"Seeded {len(manager.habits)} habits, window ending {FIXTURE_END}:")
    for h in manager.habits:
        print(
            f"  {h.name:<18} {h.frequency:<7} "
            f"entries={len(h.log):<3} "
            f"longest={h.calculate_longest_streak()}"
        )