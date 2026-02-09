from datetime import datetime, timedelta
import pandas as pd


class Habit:
    """One habit plus all the logs and streak logic around it."""

    def __init__(self, name, category, frequency, unit="count"):
        self.name = name
        self.category = category
        self.frequency = frequency
        self.unit = unit
        self.log = []

    def log_progress(self, value, note=""):
        """Add one progress entry with a number and an optional note."""
        entry = {
            "timestamp": datetime.now(),
            "value": float(value),
            "unit": self.unit,
            "note": note
        }
        self.log.append(entry)

    def get_stats(self):
        """Quick summary: how many logs we have and the latest one."""
        return {
            "total_entries": len(self.log),
            "last_entry": self.log[-1] if self.log else None
        }

    def show_log(self):
        """Return the full log as readable text so it can be printed fast."""
        if not self.log:
            return "No entries yet"

        logs = ""
        for index, entry in enumerate(self.log, 1):
            time_str = entry["timestamp"].strftime("%d/%m/%Y %H:%M")
            note_part = f" ({entry['note']})" if entry.get("note") else ""
            logs += f"{index}. [{time_str}] - {entry['value']} {entry.get('unit', self.unit)}{note_part}\n"
        return logs

    def save_log_to_file(self, filename):
        """Dump the log into a text file if you want an offline copy."""
        if not self.log:
            print(f"No entries to save for {self.name}")
            return

        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"---Habit Log: {self.name}---\n\n")
            for index, entry in enumerate(self.log, 1):
                time_str = entry["timestamp"].strftime("%d/%m/%Y %H:%M")
                note_part = f" ({entry['note']})" if entry.get("note") else ""
                file.write(f"{index}. [{time_str}] - {entry['value']} {entry.get('unit', self.unit)}{note_part}\n")

        print(f"Log for '{self.name}' saved to '{filename}'")

    def get_logs_as_dataframe(self):
        """Group logs by date and return a DataFrame ready for charts."""
        if not self.log:
            return pd.DataFrame(columns=["Date", "Value"])

        daily_totals = {}
        for entry in self.log:
            day = entry["timestamp"].date()
            daily_totals[day] = daily_totals.get(day, 0.0) + float(entry.get("value", 0.0))

        return pd.DataFrame({
            "Date": sorted(daily_totals.keys()),
            "Value": [daily_totals[day] for day in sorted(daily_totals.keys())]
        })

    def get_total_value(self):
        """Total progress value across all entries for this habit."""
        return sum(float(entry.get("value", 0.0)) for entry in self.log)

    def calculate_streak(self):
        """Current streak from today backwards (daily or weekly)."""
        if not self.log:
            return 0

        streak = 0
        today = datetime.now().date()

        if self.frequency == "Daily":
            dates = sorted({entry["timestamp"].date() for entry in self.log}, reverse=True)
            for i, date in enumerate(dates):
                expected_date = today - timedelta(days=i)
                if date == expected_date:
                    streak += 1
                else:
                    break
            return streak

        week_start_dates = sorted({
            entry["timestamp"].date() - timedelta(days=entry["timestamp"].date().weekday())
            for entry in self.log
        }, reverse=True)
        current_week_start = today - timedelta(days=today.weekday())

        for i, week_start in enumerate(week_start_dates):
            expected_week_start = current_week_start - timedelta(weeks=i)
            if week_start == expected_week_start:
                streak += 1
            else:
                break
        return streak

    def calculate_longest_streak(self):
        """Best streak ever recorded for this habit."""
        if not self.log:
            return 0

        longest = 1
        current = 1
        if self.frequency == "Daily":
            dates = sorted({entry["timestamp"].date() for entry in self.log})
            for i in range(1, len(dates)):
                if dates[i] == dates[i - 1] + timedelta(days=1):
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1
        else:
            week_start_dates = sorted({
                entry["timestamp"].date() - timedelta(days=entry["timestamp"].date().weekday())
                for entry in self.log
            })
            for i in range(1, len(week_start_dates)):
                if week_start_dates[i] - week_start_dates[i - 1] == timedelta(weeks=1):
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1
        return longest


class HabitManager:
    """Simple in-memory manager for creating, editing, and searching habits."""

    def __init__(self):
        self.habits = []
        self.predefined_habits = [
            Habit("Workout", "Health", "Daily", "reps"),
            Habit("Read a book", "Growth", "Daily", "pages"),
            Habit("Clean the house", "Productivity", "Weekly", "minutes"),
            Habit("Meditate", "Health", "Daily", "minutes"),
            Habit("Grocery Shopping", "Productivity", "Weekly", "count")
        ]
        self.habits.extend(self.predefined_habits)

    def create_habit(self, name, category, frequency, unit="count"):
        """Create a habit and keep it in the active list."""
        new_habit = Habit(name, category, frequency, unit)
        self.habits.append(new_habit)
        return new_habit

    def log_habit(self, habit_name, value, note=""):
        """Log progress for a habit by name. Returns True if it worked."""
        for habit in self.habits:
            if habit.name == habit_name:
                habit.log_progress(value, note)
                return True
        return False

    def analyse_habit(self, habit_name):
        """Return stats for one habit by name, or None if missing."""
        for habit in self.habits:
            if habit.name == habit_name:
                return habit.get_stats()
        return None

    def get_habit_names(self):
        """Return all habit names in the current manager."""
        return [habit.name for habit in self.habits]

    def get_habit_by_name(self, name):
        """Find one habit by exact name."""
        for habit in self.habits:
            if habit.name == name:
                return habit
        return None

    def update_habit(self, current_name, new_name, category, frequency, unit):
        """Edit a habit in one shot: name, category, frequency, and unit."""
        habit = self.get_habit_by_name(current_name)
        if habit is None:
            return False, "Habit not found."

        normalized_name = new_name.strip()
        normalized_unit = unit.strip()
        if not normalized_name:
            return False, "Habit name is required."
        if not normalized_unit:
            return False, "Unit is required."
        if frequency not in {"Daily", "Weekly"}:
            return False, "Frequency must be Daily or Weekly."

        existing = self.get_habit_by_name(normalized_name)
        if existing is not None and existing is not habit:
            return False, f"Habit '{normalized_name}' already exists."

        habit.name = normalized_name
        habit.category = category
        habit.frequency = frequency
        habit.unit = normalized_unit
        for entry in habit.log:
            entry["unit"] = normalized_unit
        return True, "Habit updated successfully."

    def get_habits_by_periodicity(self, frequency):
        """Get all habits that match the requested frequency."""
        return [
            habit for habit in self.habits
            if habit.frequency.lower() == frequency.lower()
        ]

    def get_longest_run_streak(self):
        """Return the highest longest-streak value across all habits."""
        if not self.habits:
            return 0
        return max(habit.calculate_longest_streak() for habit in self.habits)
