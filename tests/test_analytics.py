import unittest
from datetime import date, datetime, timedelta

import analytics
from backend import Habit


def entry(day, value=1.0):
    """Build one minimal log entry for a given date.

    The analytics functions only ever read ``entry["timestamp"]``, so the tests
    can stay focused and do not need full, realistic log entries.
    """
    return {
        "timestamp": datetime.combine(day, datetime.min.time()),
        "value": value,
        "unit": "count",
        "completed": None,
        "note": "",
    }


def log_for(days):
    """Build a log from a list of dates."""
    return [entry(day) for day in days]


class PeriodStartTests(unittest.TestCase):
    """The building blocks that turn a raw log into period-start dates."""

    def test_day_of_drops_the_time(self):
        stamp = {"timestamp": datetime(2026, 3, 4, 21, 45)}
        self.assertEqual(analytics.day_of(stamp), date(2026, 3, 4))

    def test_week_start_of_returns_monday(self):
        # 2026-03-04 is a Wednesday; its week starts Monday 2026-03-02.
        wednesday = {"timestamp": datetime(2026, 3, 4, 21, 45)}
        self.assertEqual(analytics.week_start_of(wednesday), date(2026, 3, 2))

    def test_week_start_of_monday_is_itself(self):
        monday = {"timestamp": datetime(2026, 3, 2, 8, 0)}
        self.assertEqual(analytics.week_start_of(monday), date(2026, 3, 2))

    def test_week_start_of_sunday_looks_back_to_monday(self):
        sunday = {"timestamp": datetime(2026, 3, 8, 23, 59)}
        self.assertEqual(analytics.week_start_of(sunday), date(2026, 3, 2))

    def test_period_starts_daily_dedupes_and_sorts(self):
        # Two entries on the same day must collapse into one period, and the
        # result must come back in ascending order regardless of input order.
        log = log_for([date(2026, 3, 3), date(2026, 3, 1), date(2026, 3, 3)])
        self.assertEqual(
            analytics.period_starts(log, "Daily"),
            [date(2026, 3, 1), date(2026, 3, 3)],
        )

    def test_period_starts_weekly_collapses_a_whole_week(self):
        # Wednesday and Friday of the same week are one weekly period.
        log = log_for([date(2026, 3, 4), date(2026, 3, 6), date(2026, 3, 9)])
        self.assertEqual(
            analytics.period_starts(log, "Weekly"),
            [date(2026, 3, 2), date(2026, 3, 9)],
        )

    def test_period_starts_of_empty_log_is_empty(self):
        self.assertEqual(analytics.period_starts([], "Daily"), [])

    def test_period_starts_does_not_modify_the_log(self):
        # Purity check: the function must not reorder or mutate its input.
        log = log_for([date(2026, 3, 3), date(2026, 3, 1)])
        before = [item["timestamp"] for item in log]
        analytics.period_starts(log, "Daily")
        after = [item["timestamp"] for item in log]
        self.assertEqual(before, after)


class LongestStreakTests(unittest.TestCase):
    """longest_streak: the best run of consecutive periods anywhere in a log."""

    def test_empty_log_has_no_streak(self):
        self.assertEqual(analytics.longest_streak([], "Daily"), 0)

    def test_single_entry_is_a_streak_of_one(self):
        self.assertEqual(analytics.longest_streak(log_for([date(2026, 3, 1)]), "Daily"), 1)

    def test_daily_counts_consecutive_days(self):
        log = log_for([date(2026, 3, 1), date(2026, 3, 2), date(2026, 3, 3)])
        self.assertEqual(analytics.longest_streak(log, "Daily"), 3)

    def test_daily_gap_resets_and_the_best_run_wins(self):
        # 1,2,3 is a run of 3; then a gap; then 6,7 is a run of 2.
        log = log_for([
            date(2026, 3, 1), date(2026, 3, 2), date(2026, 3, 3),
            date(2026, 3, 6), date(2026, 3, 7),
        ])
        self.assertEqual(analytics.longest_streak(log, "Daily"), 3)

    def test_daily_best_run_is_found_even_when_it_is_last(self):
        # Guards against only ever remembering the first run.
        log = log_for([
            date(2026, 3, 1), date(2026, 3, 2),
            date(2026, 3, 5), date(2026, 3, 6), date(2026, 3, 7), date(2026, 3, 8),
        ])
        self.assertEqual(analytics.longest_streak(log, "Daily"), 4)

    def test_daily_twice_in_one_day_is_still_one_period(self):
        log = [entry(date(2026, 3, 1)), entry(date(2026, 3, 1)), entry(date(2026, 3, 2))]
        self.assertEqual(analytics.longest_streak(log, "Daily"), 2)

    def test_daily_unsorted_input_gives_the_same_answer(self):
        log = log_for([date(2026, 3, 3), date(2026, 3, 1), date(2026, 3, 2)])
        self.assertEqual(analytics.longest_streak(log, "Daily"), 3)

    def test_daily_across_a_month_boundary(self):
        # 31 Mar -> 1 Apr is consecutive even though the month number changes.
        log = log_for([date(2026, 3, 31), date(2026, 4, 1), date(2026, 4, 2)])
        self.assertEqual(analytics.longest_streak(log, "Daily"), 3)

    def test_weekly_counts_consecutive_weeks(self):
        log = log_for([date(2026, 3, 2), date(2026, 3, 9), date(2026, 3, 16)])
        self.assertEqual(analytics.longest_streak(log, "Weekly"), 3)

    def test_weekly_gap_resets_the_run(self):
        # Weeks of 2 Mar and 9 Mar, then 23 Mar is skipped a week later.
        log = log_for([date(2026, 3, 2), date(2026, 3, 9), date(2026, 3, 23)])
        self.assertEqual(analytics.longest_streak(log, "Weekly"), 2)

    def test_weekly_different_weekdays_still_count_as_consecutive(self):
        # Wednesday, then the following Sunday, then the Monday after that:
        # three different weekdays but three consecutive weeks.
        log = log_for([date(2026, 3, 4), date(2026, 3, 15), date(2026, 3, 16)])
        self.assertEqual(analytics.longest_streak(log, "Weekly"), 3)

    def test_weekly_two_entries_in_one_week_do_not_inflate_the_streak(self):
        log = log_for([date(2026, 3, 2), date(2026, 3, 4), date(2026, 3, 6)])
        self.assertEqual(analytics.longest_streak(log, "Weekly"), 1)


class CurrentStreakTests(unittest.TestCase):
    """current_streak: the run counting backwards from the current period."""

    def test_empty_log_has_no_current_streak(self):
        self.assertEqual(analytics.current_streak([], "Daily", today=date(2026, 3, 10)), 0)

    def test_daily_counts_back_from_today(self):
        today = date(2026, 3, 10)
        log = log_for([today, today - timedelta(days=1), today - timedelta(days=2)])
        self.assertEqual(analytics.current_streak(log, "Daily", today=today), 3)

    def test_daily_streak_is_zero_when_today_is_missing(self):
        # The run ended yesterday, so the *current* streak is broken.
        today = date(2026, 3, 10)
        log = log_for([today - timedelta(days=1), today - timedelta(days=2)])
        self.assertEqual(analytics.current_streak(log, "Daily", today=today), 0)

    def test_daily_stops_at_the_first_gap(self):
        today = date(2026, 3, 10)
        log = log_for([
            today, today - timedelta(days=1),
            today - timedelta(days=4), today - timedelta(days=5),
        ])
        self.assertEqual(analytics.current_streak(log, "Daily", today=today), 2)

    def test_weekly_counts_back_from_this_week(self):
        today = date(2026, 3, 11)  # a Wednesday
        log = log_for([today, today - timedelta(weeks=1), today - timedelta(weeks=2)])
        self.assertEqual(analytics.current_streak(log, "Weekly", today=today), 3)

    def test_weekly_streak_is_zero_when_this_week_is_missing(self):
        today = date(2026, 3, 11)
        log = log_for([today - timedelta(weeks=1), today - timedelta(weeks=2)])
        self.assertEqual(analytics.current_streak(log, "Weekly", today=today), 0)


class CollectionAnalyticsTests(unittest.TestCase):
    """The four analytics required by the assignment, across many habits."""

    def setUp(self):
        today = date(2026, 3, 10)
        self.today = today

        self.workout = Habit("Workout", "Health", "Daily", "reps", "numeric")
        self.workout.log = log_for([
            today, today - timedelta(days=1), today - timedelta(days=2),
        ])

        self.read = Habit("Read a book", "Growth", "Daily", "pages", "numeric")
        self.read.log = log_for([today, today - timedelta(days=3)])

        self.clean = Habit("Clean the house", "Productivity", "Weekly", "completion", "boolean")
        self.clean.log = log_for([
            today, today - timedelta(weeks=1),
            today - timedelta(weeks=2), today - timedelta(weeks=3),
        ])

        self.habits = [self.workout, self.read, self.clean]

    def test_get_tracked_habits_returns_every_name(self):
        self.assertEqual(
            analytics.get_tracked_habits(self.habits),
            ["Workout", "Read a book", "Clean the house"],
        )

    def test_get_tracked_habits_of_nothing_is_empty(self):
        self.assertEqual(analytics.get_tracked_habits([]), [])

    def test_get_habits_by_periodicity_daily(self):
        daily = analytics.get_habits_by_periodicity(self.habits, "Daily")
        self.assertEqual([habit.name for habit in daily], ["Workout", "Read a book"])

    def test_get_habits_by_periodicity_weekly(self):
        weekly = analytics.get_habits_by_periodicity(self.habits, "Weekly")
        self.assertEqual([habit.name for habit in weekly], ["Clean the house"])

    def test_get_habits_by_periodicity_ignores_case(self):
        daily = analytics.get_habits_by_periodicity(self.habits, "daily")
        self.assertEqual([habit.name for habit in daily], ["Workout", "Read a book"])

    def test_get_longest_streak_all_picks_the_best_habit(self):
        # Clean the house has 4 consecutive weeks; nothing else beats it.
        self.assertEqual(analytics.get_longest_streak_all(self.habits), 4)

    def test_get_longest_streak_all_of_nothing_is_zero(self):
        self.assertEqual(analytics.get_longest_streak_all([]), 0)

    def test_get_longest_streak_for_named_habit(self):
        self.assertEqual(analytics.get_longest_streak_for(self.habits, "Workout"), 3)

    def test_get_longest_streak_for_unknown_habit_is_zero(self):
        self.assertEqual(analytics.get_longest_streak_for(self.habits, "Nope"), 0)

    def test_analytics_do_not_modify_the_habits(self):
        # Purity check at collection level: nothing gets reordered or dropped.
        names_before = [habit.name for habit in self.habits]
        log_sizes_before = [len(habit.log) for habit in self.habits]

        analytics.get_tracked_habits(self.habits)
        analytics.get_habits_by_periodicity(self.habits, "Daily")
        analytics.get_longest_streak_all(self.habits)
        analytics.get_longest_streak_for(self.habits, "Workout")

        self.assertEqual([habit.name for habit in self.habits], names_before)
        self.assertEqual([len(habit.log) for habit in self.habits], log_sizes_before)


if __name__ == "__main__":
    unittest.main()