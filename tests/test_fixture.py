"""Tests for the 4-week example fixture produced by ``seed_data.py``.

The fixture is designed so every habit's streaks are known in advance. These
tests assert those known values, so the example data and the analytics code
verify each other. If either the data generation or a streak calculation
drifts, one of these assertions fails.

Streaks are checked as of ``FIXTURE_END`` (the fixed end of the window) rather
than the real "today", so these tests give the same result forever.
"""

import unittest

import analytics
from seed_data import seed, FIXTURE_END


class FixtureStreakTests(unittest.TestCase):
    def setUp(self):
        # Rebuild the fixture in memory; we don't rely on a file on disk.
        self.manager = seed()
        self.habits = self.manager.habits

    def test_five_predefined_habits_exist(self):
        names = analytics.get_tracked_habits(self.habits)
        self.assertEqual(
            names,
            ["Workout", "Read a book", "Clean the house", "Meditate", "Grocery Shopping"],
        )

    def test_periodicity_split_is_three_daily_two_weekly(self):
        daily = analytics.get_habits_by_periodicity(self.habits, "Daily")
        weekly = analytics.get_habits_by_periodicity(self.habits, "Weekly")
        self.assertEqual(len(daily), 3)
        self.assertEqual(len(weekly), 2)

    def test_longest_streaks_match_the_design(self):
        expected = {
            "Workout": 17,          # daily, one 3-day gap -> 8 then 17
            "Read a book": 5,       # weekdays only -> runs of 5
            "Meditate": 21,         # sparse start, then 21 straight
            "Clean the house": 4,   # all four weeks
            "Grocery Shopping": 2,  # weeks 1,2 then a skip then week 4
        }
        for name, streak in expected.items():
            with self.subTest(habit=name):
                self.assertEqual(
                    analytics.get_longest_streak_for(self.habits, name), streak
                )

    def test_current_streaks_as_of_window_end(self):
        expected = {
            "Workout": 17,          # runs unbroken to the end
            "Read a book": 0,       # window ends on an unlogged Sunday
            "Meditate": 21,         # runs unbroken to the end
            "Clean the house": 4,   # every week including the last
            "Grocery Shopping": 1,  # only the final week
        }
        for name, streak in expected.items():
            with self.subTest(habit=name):
                habit = self.manager.get_habit_by_name(name)
                self.assertEqual(
                    analytics.current_streak(habit.log, habit.frequency, today=FIXTURE_END),
                    streak,
                )

    def test_overall_longest_streak_is_meditate(self):
        # 21 (Meditate) is the highest single streak across all habits.
        self.assertEqual(analytics.get_longest_streak_all(self.habits), 21)

    def test_entry_counts_match_the_design(self):
        expected = {
            "Workout": 25,          # 28 days minus the 3-day gap
            "Read a book": 20,      # 4 weeks x 5 weekdays
            "Meditate": 24,         # 3 sparse days + 21-day run
            "Clean the house": 4,   # once per week
            "Grocery Shopping": 3,  # 4 weeks minus the skipped one
        }
        for name, count in expected.items():
            with self.subTest(habit=name):
                habit = self.manager.get_habit_by_name(name)
                self.assertEqual(len(habit.log), count)


if __name__ == "__main__":
    unittest.main()