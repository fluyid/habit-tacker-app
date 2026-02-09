import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from backend import Habit, HabitManager
from functions import generate_habit_pdf, load_habits, save_habits


class FunctionTests(unittest.TestCase):
    def test_save_and_load_habits_roundtrip(self):
        manager = HabitManager()
        manager.habits = []

        habit = Habit("Workout", "Health", "Daily", "km", "numeric")
        timestamp = datetime(2025, 1, 1, 8, 30)
        habit.log.append({"timestamp": timestamp, "value": 5.0, "completed": None, "unit": "km", "note": "Morning run"})
        manager.habits.append(habit)

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "habits.json"
            save_habits(manager, str(target))

            loaded = load_habits(str(target))

        self.assertEqual(len(loaded.habits), 1)
        loaded_habit = loaded.habits[0]
        self.assertEqual(loaded_habit.name, "Workout")
        self.assertEqual(loaded_habit.category, "Health")
        self.assertEqual(loaded_habit.frequency, "Daily")
        self.assertEqual(loaded_habit.tracking_type, "numeric")
        self.assertEqual(loaded_habit.unit, "km")
        self.assertEqual(loaded_habit.log[0]["note"], "Morning run")
        self.assertEqual(loaded_habit.log[0]["value"], 5.0)
        self.assertEqual(loaded_habit.log[0]["timestamp"], timestamp)

    def test_backward_compatibility_for_old_log_format(self):
        manager = HabitManager()
        manager.habits = []

        habit = Habit("Meditate", "Health", "Daily", "minutes", "numeric")
        timestamp = datetime(2025, 1, 1, 8, 30)
        habit.log.append({"timestamp": timestamp, "note": "legacy"})
        manager.habits.append(habit)

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "habits.json"
            save_habits(manager, str(target))
            loaded = load_habits(str(target))

        self.assertEqual(loaded.habits[0].log[0]["value"], 0.0)
        self.assertEqual(loaded.habits[0].log[0]["unit"], "minutes")

    def test_boolean_habit_roundtrip(self):
        manager = HabitManager()
        manager.habits = []

        habit = Habit("Clean", "Productivity", "Weekly", "completion", "boolean")
        timestamp = datetime(2025, 1, 1, 8, 30)
        habit.log.append({"timestamp": timestamp, "value": 1.0, "completed": True, "unit": "completion", "note": "Done"})
        manager.habits.append(habit)

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "habits.json"
            save_habits(manager, str(target))
            loaded = load_habits(str(target))

        loaded_habit = loaded.habits[0]
        self.assertEqual(loaded_habit.tracking_type, "boolean")
        self.assertTrue(loaded_habit.log[0]["completed"])
        self.assertEqual(loaded_habit.log[0]["value"], 1.0)

    def test_generate_habit_pdf_returns_data(self):
        habit = Habit("Workout", "Health", "Daily", "km", "numeric")
        habit.log_progress(value=5, note="Evening run")

        try:
            pdf_data = generate_habit_pdf(habit)
        except ModuleNotFoundError:
            self.skipTest("fpdf is not installed in this Python environment")

        self.assertIsInstance(pdf_data, (bytes, bytearray))
        self.assertGreater(len(pdf_data), 100)
        self.assertTrue(pdf_data.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
