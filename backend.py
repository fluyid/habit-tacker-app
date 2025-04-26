# Creating a Habit instance
# Create User
# Create Habits class
# Create classes for different kinds of habits - Health, Productivity, Learning and Growth, Financial Habits,
# social and relationship habits, spiritual and mindfulness, create habits

from datetime import datetime


# class Habit:
#     habits = [["Run", "Health", "Daily"], ["Study", "Productivity", "Daily"], ["Clean", "Productivity", "Weekly"]]
#
#
# class NewHabit(Habit):
#     def __init__(self):
#         super().__init__()
#         # self.name = name
#         # self.category = category
#         # self.frequency = frequency
#         # self.habit = [name, category, frequency]
#         # self.habits.append(self.habit)
#         self.streak = 0
#
#     # def create_habit(self):
#     #     new_habits = [self.name, self.category, self.frequency]
#     #     self.habits.append(new_habits)
#
#     def add_a_new_habit(self, name, category, frequency):
#         new_habit = [name, category, frequency]
#         self.habits.append(new_habit)
#
#     def complete(self):
#         self.streak += 1
#         print(f"Nice you are on a {self.streak} day streak")

# Test
# kai_habits = NewHabit()
# kai_habits.add_a_new_habit("Drink Water", "Health", "Daily")
#
# print(kai_habits.habits)

class Habit:
    def __init__(self, name, category, frequency):
        self.name = name
        self.category = category
        self.frequency = frequency
        self.log = []

    def log_progress(self, note):
        entry = {
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "note": note
        }
        self.log.append(entry)

    def get_stats(self):
        return {
            "total_entries": len(self.log),
            "last_entry": self.log[-1] if self.log else None
        }

    def show_log(self):
        if not self.log:
            print(f"No entries for habit '{self.name}'")
            return

        print(f"\n----Log for '{self.name}'-----")
        for index, entry in enumerate(self.log, 1):
            time_str = entry["timestamp"]
            print(f"{index}. [{time_str}] - {entry["note"]}")

    def save_log_to_file(self, filename):
        if not self.log:
            print(f"No entries to save for {self.name}")
            return

        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"---Habit Log: {self.name}---\n\n")
            for index, entry in enumerate(self.log, 1):
                time_str = entry["timestamp"]
                file.write(f"{index}. [{time_str}] - {entry["note"]}\n")

        print(f"Log for '{self.name}' saved to '{filename}'")


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


# Test
kai_habits2 = HabitManager()
new_habit = kai_habits2.create_habit(name="Drink Water", category="Health", frequency="Daily")

for habits in kai_habits2.habits:
    print(habits.name)

kai_habits2.log_habit("Drink Water", "Drank 8 glasses of water")
kai_habits2.log_habit("Workout", "Exercised for 30 minutes")

print("Habit Stats")

for habit in ["Drink Water", "Workout"]:
    stats = kai_habits2.analyse_habit(habit)
    print(f"{habit}: {stats}")

stats = kai_habits2.analyse_habit("Drink Water")
print("Habit analysis for Drink Water")
if stats["last_entry"]:
    print(f"Last Log Time: {stats["last_entry"]["timestamp"]}")
    print(f"Last Log Note: {stats["last_entry"]["note"]}")

new_habit2 = kai_habits2.create_habit(
    name="Practice Piano",
    category="Growth",
    frequency="Daily"
)

kai_habits2.log_habit("Practice Piano", "Practiced 'Sadness and Sorrow'")
kai_habits2.log_habit("Practice Piano", "Practiced Heaven Shaking")
kai_habits2.log_habit("Practice Piano", "Practiced Star Walking")

for habits in kai_habits2.habits:
    habits.show_log()

for habits in kai_habits2.habits:
    habits.save_log_to_file(f"{habits.name}.txt")
