import unittest
from datetime import datetime, timedelta

from backend import Habit, HabitManager


class HabitTests(unittest.TestCase):
    def test_log_progress_and_stats(self):
        habit = Habit("Drink Water", "Health", "Daily", "ml")
        habit.log_progress(500, "Morning hydration")

        stats = habit.get_stats()
        self.assertEqual(stats["total_entries"], 1)
        self.assertEqual(stats["last_entry"]["note"], "Morning hydration")
        self.assertEqual(stats["last_entry"]["value"], 500.0)
        self.assertEqual(stats["last_entry"]["unit"], "ml")

    def test_show_log_without_entries(self):
        habit = Habit("Meditate", "Health", "Daily", "minutes")
        self.assertEqual(habit.show_log(), "No entries yet")

    def test_get_total_value(self):
        habit = Habit("Run", "Health", "Daily", "km")
        habit.log_progress(3)
        habit.log_progress(2.5)
        self.assertEqual(habit.get_total_value(), 5.5)

    def test_calculate_streak_daily(self):
        habit = Habit("Workout", "Health", "Daily", "reps")
        today = datetime.now().date()

        for delta_days in [0, 1, 2, 4]:
            habit.log.append({
                "timestamp": datetime.combine(today - timedelta(days=delta_days), datetime.min.time()),
                "value": 1.0,
                "unit": "reps",
                "note": "done",
            })

        self.assertEqual(habit.calculate_streak(), 3)

    def test_calculate_streak_weekly(self):
        habit = Habit("Clean", "Productivity", "Weekly", "minutes")
        today = datetime.now().date()

        for delta_weeks in [0, 1, 2, 4]:
            habit.log.append({
                "timestamp": datetime.combine(today - timedelta(weeks=delta_weeks), datetime.min.time()),
                "value": 1.0,
                "unit": "minutes",
                "note": "done",
            })

        self.assertEqual(habit.calculate_streak(), 3)

    def test_calculate_longest_streak_daily(self):
        habit = Habit("Read", "Growth", "Daily", "pages")
        base = datetime.now().date()

        for delta_days in [10, 9, 8, 5, 4]:
            habit.log.append({
                "timestamp": datetime.combine(base - timedelta(days=delta_days), datetime.min.time()),
                "value": 1.0,
                "unit": "pages",
                "note": "done",
            })

        self.assertEqual(habit.calculate_longest_streak(), 3)

    def test_calculate_longest_streak_weekly(self):
        habit = Habit("Groceries", "Productivity", "Weekly", "count")
        base = datetime.now().date()

        for delta_weeks in [8, 7, 6, 3, 2]:
            habit.log.append({
                "timestamp": datetime.combine(base - timedelta(weeks=delta_weeks), datetime.min.time()),
                "value": 1.0,
                "unit": "count",
                "note": "done",
            })

        self.assertEqual(habit.calculate_longest_streak(), 3)


class HabitManagerTests(unittest.TestCase):
    def test_get_habits_by_periodicity(self):
        manager = HabitManager()
        manager.habits = []
        manager.create_habit("Workout", "Health", "Daily", "reps")
        manager.create_habit("Clean", "Productivity", "Weekly", "minutes")

        daily_habits = manager.get_habits_by_periodicity("daily")
        self.assertEqual([habit.name for habit in daily_habits], ["Workout"])

    def test_get_longest_run_streak(self):
        manager = HabitManager()
        manager.habits = []

        daily_habit = manager.create_habit("Workout", "Health", "Daily", "reps")
        weekly_habit = manager.create_habit("Clean", "Productivity", "Weekly", "minutes")
        today = datetime.now().date()

        for delta_days in [0, 1, 2]:
            daily_habit.log.append({
                "timestamp": datetime.combine(today - timedelta(days=delta_days), datetime.min.time()),
                "value": 1.0,
                "unit": "reps",
                "note": "done",
            })

        for delta_weeks in [0, 2]:
            weekly_habit.log.append({
                "timestamp": datetime.combine(today - timedelta(weeks=delta_weeks), datetime.min.time()),
                "value": 1.0,
                "unit": "minutes",
                "note": "done",
            })

        self.assertEqual(manager.get_longest_run_streak(), 3)

    def test_update_habit_all_fields(self):
        manager = HabitManager()
        manager.habits = []
        manager.create_habit("Run", "Health", "Daily", "km")

        ok, message = manager.update_habit(
            current_name="Run",
            new_name="Morning Run",
            category="Productivity",
            frequency="Weekly",
            unit="minutes"
        )

        self.assertTrue(ok)
        self.assertEqual(message, "Habit updated successfully.")
        updated = manager.get_habit_by_name("Morning Run")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.category, "Productivity")
        self.assertEqual(updated.frequency, "Weekly")
        self.assertEqual(updated.unit, "minutes")

    def test_update_habit_duplicate_name_fails(self):
        manager = HabitManager()
        manager.habits = []
        manager.create_habit("Run", "Health", "Daily", "km")
        manager.create_habit("Walk", "Health", "Daily", "km")

        ok, message = manager.update_habit(
            current_name="Run",
            new_name="Walk",
            category="Health",
            frequency="Daily",
            unit="km"
        )

        self.assertFalse(ok)
        self.assertEqual(message, "Habit 'Walk' already exists.")


if __name__ == "__main__":
    unittest.main()
