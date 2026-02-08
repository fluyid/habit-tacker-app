from datetime import datetime, timedelta
import pandas as pd


class Habit:
    def __init__(self, name, category, frequency):
        self.name = name
        self.category = category
        self.frequency = frequency
        self.log = []

    def log_progress(self, note):
        """This method logs the progress. The note must be added by the user. However, the time would automatically
        be added. The data added here will be used for displaying the log, analysing the data and even generating
        the pdf"""
        entry = {
            "timestamp": datetime.now(),
            "note": note
        }
        self.log.append(entry)

    def get_stats(self):
        """This method would return the total number of entries as well as when was the last entry"""
        return {
            "total_entries": len(self.log),
            "last_entry": self.log[-1] if self.log else None
        }

    def show_log(self):
        """This method would return the logs of the selected habit. It would return an index number, date and time
        of the habit as well as the note that was added to it in log_progress(if any note was added)"""
        if not self.log:
            # print(f"No entries for habit '{self.name}'")
            return "No entries yet"

        # print(f"\n----Log for '{self.name}'-----")
        # for index, entry in enumerate(self.log, 1):
        #     time_str = entry["timestamp"].strftime("%d/%m/%Y %H:%M")
        #     print(f"{index}. [{time_str}] - {entry["note"]}")
        logs = ""
        for index, entry in enumerate(self.log, 1):
            time_str = entry["timestamp"].strftime("%d/%m/%Y %H:%M")
            logs += f"{index}. [{time_str}] - {entry['note']}\n"
        return logs

    def save_log_to_file(self, filename):
        """This method would save the logs of a habit to a text file."""
        if not self.log:
            print(f"No entries to save for {self.name}")
            return

        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"---Habit Log: {self.name}---\n\n")
            for index, entry in enumerate(self.log, 1):
                time_str = entry["timestamp"].strftime("%d/%m/%Y %H:%M")
                file.write(f"{index}. [{time_str}] - {entry["note"]}\n")

        print(f"Log for '{self.name}' saved to '{filename}'")

    def get_logs_as_dataframe(self):
        """This method converts the log in to a dataframe so that it can be used to plot graphs"""
        if not self.log:
            return pd.DataFrame(columns=["Date", "Entries"])

        dates = [entry["timestamp"].date() for entry in self.log]
        date_counts = pd.Series(dates).value_counts().sort_index()
        # print(date_counts)
        # print(date_counts.index)
        # print(date_counts.values)

        df = pd.DataFrame({
            "Date": date_counts.index,
            "Entries": date_counts.values
        })
        return df

    def calculate_streak(self):
        """Calculates the streak for daily and weekly tasks. Streak is increased by 1 if the habit is performed daily
        but for weekly the habit need to be performed only once per week. For example, if a habit is performed on last
        sunday, performing it this Sunday would increase it by 1 but performing it on any other days won't."""
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
    def __init__(self):
        self.habits = []
        self.predefined_habits = [
            Habit("Workout", "Health", "Daily"),
            Habit("Read a book", "Growth", "Daily"),
            Habit("Clean the house", "Productivity", "Weekly"),
            Habit("Meditate", "Health", "Daily"),
            Habit("Grocery Shopping", "Productivity", "Weekly")
        ]
        self.habits.extend(self.predefined_habits)

    def create_habit(self, name, category, frequency):
        new_habit = Habit(name, category, frequency)
        self.habits.append(new_habit)
        return new_habit

    def log_habit(self, habit_name, entry):
        for habit in self.habits:
            if habit.name == habit_name:
                habit.log_progress(entry)
                return True
        return False

    def analyse_habit(self, habit_name):
        for habit in self.habits:
            if habit.name == habit_name:
                return habit.get_stats()
        return None

    def get_habit_names(self):
        return [habit.name for habit in self.habits]

    def get_habit_by_name(self, name):
        for habit in self.habits:
            if habit.name == name:
                return habit
        return None

    def get_habits_by_periodicity(self, frequency):
        return [
            habit for habit in self.habits
            if habit.frequency.lower() == frequency.lower()
        ]

    def get_longest_run_streak(self):
        if not self.habits:
            return 0
        return max(habit.calculate_longest_streak() for habit in self.habits)


# Test
# kai_habits2 = HabitManager()
# new_habit = kai_habits2.create_habit(name="Drink Water", category="Health", frequency="Daily")
#
# for habits in kai_habits2.habits:
#     print(habits.name)
#
# kai_habits2.log_habit("Drink Water", "Drank 8 glasses of water")
# kai_habits2.log_habit("Workout", "Exercised for 30 minutes")
#
# print("Habit Stats")
#
# for habit in ["Drink Water", "Workout"]:
#     stats = kai_habits2.analyse_habit(habit)
#     print(f"{habit}: {stats}")
#
# stats = kai_habits2.analyse_habit("Drink Water")
# print("Habit analysis for Drink Water")
# if stats["last_entry"]:
#     print(f"Last Log Time: {stats["last_entry"]["timestamp"]}")
#     print(f"Last Log Note: {stats["last_entry"]["note"]}")
#
# new_habit2 = kai_habits2.create_habit(
#     name="Practice Piano",
#     category="Growth",
#     frequency="Daily"
# )
#
# kai_habits2.log_habit("Practice Piano", "Practiced 'Sadness and Sorrow'")
# kai_habits2.log_habit("Practice Piano", "Practiced Heaven Shaking")
# kai_habits2.log_habit("Practice Piano", "Practiced Star Walking")
#
# for habits in kai_habits2.habits:
#     habits.show_log()
#
# for habits in kai_habits2.habits:
#     habits.save_log_to_file(f"{habits.name}.txt")
