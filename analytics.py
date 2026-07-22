"""Functional analytics for the habit tracker.

Every function here is *pure*: it takes data as an argument and returns a
result without changing anything it was given and without touching any shared
state. Given the same input, each function always returns the same output.

The module intentionally depends on nothing from ``backend.py`` -- it only
knows about plain lists of habits and their log entries. That one-way
dependency (backend imports analytics, never the reverse) keeps the analysis
logic testable in isolation and avoids circular imports.

The building blocks (``day_of``, ``week_start_of``, ``period_starts``) turn a
raw log into a sorted list of "period start" dates. Everything else is
expressed with ``filter``, ``map``, ``functools.reduce`` and comprehensions on
top of those blocks.
"""

from datetime import date, timedelta
from functools import reduce


# Building blocks: raw log  ->  sorted period-start dates


def day_of(entry):
    """Return the calendar date of one log entry.

    ``entry["timestamp"]`` is a ``datetime``; we drop the time-of-day so that
    two entries on the same day collapse to the same period.
    """
    return entry["timestamp"].date()


def week_start_of(entry):
    """Return the Monday that begins the week containing this entry.

    ``weekday()`` is 0 for Monday .. 6 for Sunday, so subtracting it from the
    entry's date always lands on that week's Monday. This makes every entry in
    the same Mon-Sun week collapse to one shared date.
    """
    d = day_of(entry)
    return d - timedelta(days=d.weekday())


def period_starts(log, frequency):
    """Collapse a log into a sorted list of unique period-start dates.

    For a ``Daily`` habit each period is a day; for a ``Weekly`` habit each
    period is a Mon-Sun week represented by its Monday. Duplicates within a
    period are removed (via ``set``) and the result is sorted ascending.

    This single function replaces the four near-identical set-comprehensions
    that used to live inside the streak methods.
    """
    if not log:
        return []
    key = day_of if frequency == "Daily" else week_start_of
    return sorted({key(entry) for entry in log})


def _step(frequency):
    """The gap between two consecutive periods: one day, or one week."""
    return timedelta(days=1) if frequency == "Daily" else timedelta(weeks=1)


# --------------------------------------------------------------------------- #
# Streaks (pure functions over a single habit's log)
# --------------------------------------------------------------------------- #

def longest_streak(log, frequency):
    """Longest run of consecutive periods anywhere in the log.

    We walk the sorted period starts and fold them into a running
    ``(best, current, previous)`` state with ``reduce``. Each period that sits
    exactly one step after the previous one extends the current run; any gap
    resets it to 1. ``best`` remembers the longest run seen.
    """
    starts = period_starts(log, frequency)
    if not starts:
        return 0

    step = _step(frequency)

    def fold(state, current_start):
        best, run, previous = state
        run = run + 1 if current_start - previous == step else 1
        return (max(best, run), run, current_start)

    # Seed with the first period already counted, then fold the rest.
    best, _, _ = reduce(fold, starts[1:], (1, 1, starts[0]))
    return best


def current_streak(log, frequency, today=None):
    """Streak counting backwards from the current period.

    We look at the period starts newest-first and check them against the
    expected sequence (this period, one step back, two steps back, ...). The
    first gap stops the count. ``today`` is injectable so tests can pin "now".
    """
    starts = sorted(period_starts(log, frequency), reverse=True)
    if not starts:
        return 0

    today = today or date.today()
    step = _step(frequency)
    if frequency == "Daily":
        current_period = today
    else:
        current_period = today - timedelta(days=today.weekday())

    streak = 0
    for i, start in enumerate(starts):
        if start == current_period - step * i:
            streak += 1
        else:
            break
    return streak


# Collection-level analytics (pure functions over a list of habits)

def get_tracked_habits(habits):
    """Return the names of all currently tracked habits."""
    return list(map(lambda h: h.name, habits))


def get_habits_by_periodicity(habits, frequency):
    """Return the habits whose frequency matches (case-insensitive)."""
    return list(filter(lambda h: h.frequency.lower() == frequency.lower(), habits))


def get_longest_streak_all(habits):
    """Return the single best longest-streak across every habit (0 if none)."""
    streaks = map(lambda h: longest_streak(h.log, h.frequency), habits)
    return reduce(max, streaks, 0)


def get_longest_streak_for(habits, name):
    """Return the longest streak for one habit by name (0 if not found)."""
    match = next(filter(lambda h: h.name == name, habits), None)
    return longest_streak(match.log, match.frequency) if match else 0