import unittest
from datetime import datetime, timedelta

from backend import Habit, HabitManager


class HabitTests(unittest.TestCase):
    def test_log_progress_and_stats(self):
        habit = Habit("Drink Water", "Health", "Daily")
        habit.log_progress("8 glasses")

        stats = habit.get_stats()
        self.assertEqual(stats["total_entries"], 1)
        self.assertEqual(stats["last_entry"]["note"], "8 glasses")

    def test_show_log_without_entries(self):
        habit = Habit("Meditate", "Health", "Daily")
        self.assertEqual(habit.show_log(), "No entries yet")

    def test_calculate_streak_daily(self):
        habit = Habit("Workout", "Health", "Daily")
        today = datetime.now().date()

        for delta_days in [0, 1, 2, 4]:
            habit.log.append({
                "timestamp": datetime.combine(today - timedelta(days=delta_days), datetime.min.time()),
                "note": "done",
            })

        self.assertEqual(habit.calculate_streak(), 3)

    def test_calculate_streak_weekly(self):
        habit = Habit("Clean", "Productivity", "Weekly")
        today = datetime.now().date()

        for delta_weeks in [0, 1, 2, 4]:
            habit.log.append({
                "timestamp": datetime.combine(today - timedelta(weeks=delta_weeks), datetime.min.time()),
                "note": "done",
            })

        self.assertEqual(habit.calculate_streak(), 3)

    def test_calculate_longest_streak_daily(self):
        habit = Habit("Read", "Growth", "Daily")
        base = datetime.now().date()

        for delta_days in [10, 9, 8, 5, 4]:
            habit.log.append({
                "timestamp": datetime.combine(base - timedelta(days=delta_days), datetime.min.time()),
                "note": "done",
            })

        self.assertEqual(habit.calculate_longest_streak(), 3)

    def test_calculate_longest_streak_weekly(self):
        habit = Habit("Groceries", "Productivity", "Weekly")
        base = datetime.now().date()

        for delta_weeks in [8, 7, 6, 3, 2]:
            habit.log.append({
                "timestamp": datetime.combine(base - timedelta(weeks=delta_weeks), datetime.min.time()),
                "note": "done",
            })

        self.assertEqual(habit.calculate_longest_streak(), 3)


class HabitManagerTests(unittest.TestCase):
    def test_get_habits_by_periodicity(self):
        manager = HabitManager()
        manager.habits = []
        manager.create_habit("Workout", "Health", "Daily")
        manager.create_habit("Clean", "Productivity", "Weekly")

        daily_habits = manager.get_habits_by_periodicity("daily")
        self.assertEqual([habit.name for habit in daily_habits], ["Workout"])

    def test_get_longest_run_streak(self):
        manager = HabitManager()
        manager.habits = []

        daily_habit = manager.create_habit("Workout", "Health", "Daily")
        weekly_habit = manager.create_habit("Clean", "Productivity", "Weekly")
        today = datetime.now().date()

        for delta_days in [0, 1, 2]:
            daily_habit.log.append({
                "timestamp": datetime.combine(today - timedelta(days=delta_days), datetime.min.time()),
                "note": "done",
            })

        for delta_weeks in [0, 2]:
            weekly_habit.log.append({
                "timestamp": datetime.combine(today - timedelta(weeks=delta_weeks), datetime.min.time()),
                "note": "done",
            })

        self.assertEqual(manager.get_longest_run_streak(), 3)


if __name__ == "__main__":
    unittest.main()
