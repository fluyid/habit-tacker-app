from datetime import datetime, timedelta
import pandas as pd
import analytics


class Habit:
    """One habit plus all the logs and streak logic around it."""

    def __init__(self, name, category, frequency, unit="count", tracking_type="numeric"):
        self.name = name
        self.category = category
        self.frequency = frequency
        self.unit = unit
        self.tracking_type = tracking_type
        self.log = []

    def log_progress(self, value=None, note="", completed=None):
        """Add one entry. Numeric habits use value, Yes/No habits use completed."""
        if self.tracking_type == "boolean":
            if completed is None:
                raise ValueError("Boolean habits need a Yes/No completion value.")
            bool_completed = bool(completed)
            numeric_value = 1.0 if bool_completed else 0.0
        else:
            if value is None:
                raise ValueError("Numeric habits need a progress value.")
            numeric_value = float(value)
            bool_completed = None

        entry = {
            "timestamp": datetime.now(),
            "value": numeric_value,
            "unit": self.unit,
            "completed": bool_completed,
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
            if self.tracking_type == "boolean":
                status = "Yes" if entry.get("completed") else "No"
                logs += f"{index}. [{time_str}] - Completed: {status}{note_part}\n"
            else:
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
                if self.tracking_type == "boolean":
                    status = "Yes" if entry.get("completed") else "No"
                    file.write(f"{index}. [{time_str}] - Completed: {status}{note_part}\n")
                else:
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

    def get_completion_counts(self):
        """For Yes/No habits, return total yes and no entries."""
        yes_count = sum(1 for entry in self.log if entry.get("completed") is True)
        no_count = sum(1 for entry in self.log if entry.get("completed") is False)
        return {"yes": yes_count, "no": no_count}

    def _has_log_for_date(self, target_date):
        return any(entry["timestamp"].date() == target_date for entry in self.log)

    def _has_log_in_week(self, reference_time):
        week_start = (reference_time - timedelta(days=reference_time.weekday())).date()
        week_end = week_start + timedelta(days=7)
        return any(week_start <= entry["timestamp"].date() < week_end for entry in self.log)

    def needs_update(self, reference_time=None):
        """Return True when this habit should show an update reminder."""
        now = reference_time or datetime.now()

        if self.frequency == "Daily":
            return not self._has_log_for_date(now.date())

        # Weekly reminder: only show in the last 48h of the week if this week has no entry.
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=7)
        reminder_start = week_end - timedelta(hours=48)
        in_reminder_window = reminder_start <= now < week_end
        if not in_reminder_window:
            return False
        return not self._has_log_in_week(now)

    def calculate_streak(self):
        # """Current streak from today backwards (daily or weekly)."""
        # if not self.log:
        #     return 0
        #
        # streak = 0
        # today = datetime.now().date()
        #
        # if self.frequency == "Daily":
        #     dates = sorted({entry["timestamp"].date() for entry in self.log}, reverse=True)
        #     for i, date in enumerate(dates):
        #         expected_date = today - timedelta(days=i)
        #         if date == expected_date:
        #             streak += 1
        #         else:
        #             break
        #     return streak
        #
        # week_start_dates = sorted({
        #     entry["timestamp"].date() - timedelta(days=entry["timestamp"].date().weekday())
        #     for entry in self.log
        # }, reverse=True)
        # current_week_start = today - timedelta(days=today.weekday())
        #
        # for i, week_start in enumerate(week_start_dates):
        #     expected_week_start = current_week_start - timedelta(weeks=i)
        #     if week_start == expected_week_start:
        #         streak += 1
        #     else:
        #         break
        # return streak
        return analytics.current_streak(self.log, self.frequency)

    def calculate_longest_streak(self):
        """Best streak ever recorded for this habit."""
        # if not self.log:
        #     return 0
        #
        # longest = 1
        # current = 1
        # if self.frequency == "Daily":
        #     dates = sorted({entry["timestamp"].date() for entry in self.log})
        #     for i in range(1, len(dates)):
        #         if dates[i] == dates[i - 1] + timedelta(days=1):
        #             current += 1
        #             longest = max(longest, current)
        #         else:
        #             current = 1
        # else:
        #     week_start_dates = sorted({
        #         entry["timestamp"].date() - timedelta(days=entry["timestamp"].date().weekday())
        #         for entry in self.log
        #     })
        #     for i in range(1, len(week_start_dates)):
        #         if week_start_dates[i] - week_start_dates[i - 1] == timedelta(weeks=1):
        #             current += 1
        #             longest = max(longest, current)
        #         else:
        #             current = 1
        # return longest
        return analytics.longest_streak(self.log, self.frequency)


class HabitManager:
    """Simple in-memory manager for creating, editing, and searching habits."""

    def __init__(self):
        self.habits = []
        self.predefined_habits = [
            Habit("Workout", "Health", "Daily", "reps", "numeric"),
            Habit("Read a book", "Growth", "Daily", "pages", "numeric"),
            Habit("Clean the house", "Productivity", "Weekly", "completion", "boolean"),
            Habit("Meditate", "Health", "Daily", "minutes", "numeric"),
            Habit("Grocery Shopping", "Productivity", "Weekly", "completion", "boolean")
        ]
        self.habits.extend(self.predefined_habits)

    def create_habit(self, name, category, frequency, unit="count", tracking_type="numeric"):
        """Create a habit and keep it in the active list."""
        new_habit = Habit(name, category, frequency, unit, tracking_type)
        self.habits.append(new_habit)
        return new_habit

    def log_habit(self, habit_name, value=None, note="", completed=None):
        """Log progress for a habit by name. Returns True if it worked."""
        for habit in self.habits:
            if habit.name == habit_name:
                habit.log_progress(value=value, note=note, completed=completed)
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

    def update_habit(self, current_name, new_name, category, frequency, unit, tracking_type):
        """Edit a habit in one shot: name, category, frequency, unit, and type."""
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
            return False, "Frequency must be Daily or Weekly"
        if tracking_type not in {"numeric", "boolean"}:
            return False, "Tracking type must be numeric or boolean"

        existing = self.get_habit_by_name(normalized_name)
        if existing is not None and existing is not habit:
            return False, f"Habit '{normalized_name}' already exists."

        habit.name = normalized_name
        habit.category = category
        habit.frequency = frequency
        habit.unit = normalized_unit
        habit.tracking_type = tracking_type
        for entry in habit.log:
            entry["unit"] = normalized_unit
            if tracking_type == "boolean":
                completed_value = entry.get("completed")
                if completed_value is None:
                    completed_value = float(entry.get("value", 0.0)) > 0
                entry["completed"] = bool(completed_value)
                entry["value"] = 1.0 if entry["completed"] else 0.0
            else:
                entry["completed"] = None
        return True, "Habit updated successfully."

    def delete_habit(self, name):
        """Delete a habit by name.

        Returns a (success, message) tuple to match update_habit so the UI can
        show feedback the same way for both actions.
        """
        habit = self.get_habit_by_name(name)
        if habit is None:
            return False, "Habit not found."
        self.habits.remove(habit)
        return True, f"Habit '{name}' deleted."

    def get_habits_by_periodicity(self, frequency):
        """Get all habits that match the requested frequency."""
        # return [
        #     habit for habit in self.habits
        #     if habit.frequency.lower() == frequency.lower()
        # ]
        return analytics.get_habits_by_periodicity(self.habits, frequency)

    def get_longest_run_streak(self):
        """Return the highest longest-streak value across all habits."""
        # if not self.habits:
        #     return 0
        # return max(habit.calculate_longest_streak() for habit in self.habits)
        return analytics.get_longest_streak_all(self.habits)
