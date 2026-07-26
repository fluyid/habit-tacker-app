import unittest
from datetime import datetime, timedelta

from backend import Habit, HabitManager


class HabitTests(unittest.TestCase):
    def test_log_progress_and_stats(self):
        habit = Habit("Drink Water", "Health", "Daily", "ml", "numeric")
        habit.log_progress(value=500, note="Morning hydration")

        stats = habit.get_stats()
        self.assertEqual(stats["total_entries"], 1)
        self.assertEqual(stats["last_entry"]["note"], "Morning hydration")
        self.assertEqual(stats["last_entry"]["value"], 500.0)
        self.assertEqual(stats["last_entry"]["unit"], "ml")

    def test_show_log_without_entries(self):
        habit = Habit("Meditate", "Health", "Daily", "minutes", "numeric")
        self.assertEqual(habit.show_log(), "No entries yet")

    def test_get_total_value(self):
        habit = Habit("Run", "Health", "Daily", "km", "numeric")
        habit.log_progress(value=3)
        habit.log_progress(value=2.5)
        self.assertEqual(habit.get_total_value(), 5.5)

    def test_calculate_streak_daily(self):
        habit = Habit("Workout", "Health", "Daily", "reps", "numeric")
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
        habit = Habit("Clean", "Productivity", "Weekly", "minutes", "numeric")
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
        habit = Habit("Read", "Growth", "Daily", "pages", "numeric")
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
        habit = Habit("Groceries", "Productivity", "Weekly", "count", "numeric")
        base = datetime.now().date()

        for delta_weeks in [8, 7, 6, 3, 2]:
            habit.log.append({
                "timestamp": datetime.combine(base - timedelta(weeks=delta_weeks), datetime.min.time()),
                "value": 1.0,
                "unit": "count",
                "note": "done",
            })

        self.assertEqual(habit.calculate_longest_streak(), 3)

    def test_boolean_habit_logs_yes_no(self):
        habit = Habit("Clean the house", "Productivity", "Weekly", "completion", "boolean")
        habit.log_progress(completed=True, note="Deep clean")
        habit.log_progress(completed=False, note="Skipped this week")

        counts = habit.get_completion_counts()
        self.assertEqual(counts["yes"], 1)
        self.assertEqual(counts["no"], 1)
        self.assertEqual(habit.get_total_value(), 1.0)

    def test_daily_needs_update(self):
        habit = Habit("Run", "Health", "Daily", "km", "numeric")
        reference = datetime(2026, 2, 9, 9, 0)
        self.assertTrue(habit.needs_update(reference))

        habit.log.append({
            "timestamp": reference - timedelta(hours=1),
            "value": 5.0,
            "completed": None,
            "unit": "km",
            "note": "morning run",
        })
        self.assertFalse(habit.needs_update(reference))

    def test_weekly_needs_update_only_in_last_48_hours(self):
        habit = Habit("Clean", "Productivity", "Weekly", "completion", "boolean")

        # Wednesday noon: outside 48-hour reminder window.
        midweek = datetime(2026, 2, 11, 12, 0)
        self.assertFalse(habit.needs_update(midweek))

        # Saturday noon: within last 48h before week end, no log yet.
        weekend_window = datetime(2026, 2, 14, 12, 0)
        self.assertTrue(habit.needs_update(weekend_window))

        # If logged this week, reminder should go away.
        habit.log.append({
            "timestamp": datetime(2026, 2, 10, 10, 0),
            "value": 1.0,
            "completed": True,
            "unit": "completion",
            "note": "done",
        })
        self.assertFalse(habit.needs_update(weekend_window))


class HabitManagerTests(unittest.TestCase):
    def test_get_habits_by_periodicity(self):
        manager = HabitManager()
        manager.habits = []
        manager.create_habit("Workout", "Health", "Daily", "reps", "numeric")
        manager.create_habit("Clean", "Productivity", "Weekly", "completion", "boolean")

        daily_habits = manager.get_habits_by_periodicity("daily")
        self.assertEqual([habit.name for habit in daily_habits], ["Workout"])

    def test_get_longest_run_streak(self):
        manager = HabitManager()
        manager.habits = []

        daily_habit = manager.create_habit("Workout", "Health", "Daily", "reps", "numeric")
        weekly_habit = manager.create_habit("Clean", "Productivity", "Weekly", "completion", "boolean")
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
                "completed": True,
                "unit": "completion",
                "note": "done",
            })

        self.assertEqual(manager.get_longest_run_streak(), 3)

    def test_update_habit_all_fields(self):
        manager = HabitManager()
        manager.habits = []
        manager.create_habit("Run", "Health", "Daily", "km", "numeric")

        ok, message = manager.update_habit(
            current_name="Run",
            new_name="Morning Run",
            category="Productivity",
            frequency="Weekly",
            unit="completion",
            tracking_type="boolean"
        )

        self.assertTrue(ok)
        self.assertEqual(message, "Habit updated successfully.")
        updated = manager.get_habit_by_name("Morning Run")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.category, "Productivity")
        self.assertEqual(updated.frequency, "Weekly")
        self.assertEqual(updated.unit, "completion")
        self.assertEqual(updated.tracking_type, "boolean")

    def test_update_habit_duplicate_name_fails(self):
        manager = HabitManager()
        manager.habits = []
        manager.create_habit("Run", "Health", "Daily", "km", "numeric")
        manager.create_habit("Walk", "Health", "Daily", "km", "numeric")

        ok, message = manager.update_habit(
            current_name="Run",
            new_name="Walk",
            category="Health",
            frequency="Daily",
            unit="km",
            tracking_type="numeric"
        )

        self.assertFalse(ok)
        self.assertEqual(message, "Habit 'Walk' already exists.")

    def test_delete_habit_removes_it(self):
        manager = HabitManager()
        manager.habits = []
        manager.create_habit("Workout", "Health", "Daily", "reps", "numeric")
        manager.create_habit("Read", "Growth", "Daily", "pages", "numeric")

        ok, _ = manager.delete_habit("Workout")

        self.assertTrue(ok)
        self.assertEqual(manager.get_habit_names(), ["Read"])

    def test_delete_habit_that_does_not_exist_fails(self):
        manager = HabitManager()
        manager.habits = []
        manager.create_habit("Read", "Growth", "Daily", "pages", "numeric")

        ok, message = manager.delete_habit("Nope")

        self.assertFalse(ok)
        self.assertEqual(manager.get_habit_names(), ["Read"])


if __name__ == "__main__":
    unittest.main()
