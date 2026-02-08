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

        habit = Habit("Workout", "Health", "Daily")
        timestamp = datetime(2025, 1, 1, 8, 30)
        habit.log.append({"timestamp": timestamp, "note": "Ran 5km"})
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
        self.assertEqual(loaded_habit.log[0]["note"], "Ran 5km")
        self.assertEqual(loaded_habit.log[0]["timestamp"], timestamp)

    def test_generate_habit_pdf_returns_data(self):
        habit = Habit("Workout", "Health", "Daily")
        habit.log_progress("Ran 5km")

        try:
            pdf_data = generate_habit_pdf(habit)
        except ModuleNotFoundError:
            self.skipTest("fpdf is not installed in this Python environment")

        self.assertIsInstance(pdf_data, (bytes, bytearray))
        self.assertGreater(len(pdf_data), 100)
        self.assertTrue(pdf_data.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
