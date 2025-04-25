# Creating a Habit instance
# Create User
# Create Habits class
# Create classes for different kinds of habits - Health, Productivity, Learning and Growth, Financial Habits,
# social and relationship habits, spiritual and mindfulness, create habits


class Habit:
    habits = [["Run", "Health", "Daily"], ["Study", "Productivity", "Daily"], ["Clean", "Productivity", "Weekly"]]


class NewHabit(Habit):
    def __init__(self):
        super().__init__()
        # self.name = name
        # self.category = category
        # self.frequency = frequency
        # self.habit = [name, category, frequency]
        # self.habits.append(self.habit)
        self.streak = 0


    # def create_habit(self):
    #     new_habits = [self.name, self.category, self.frequency]
    #     self.habits.append(new_habits)


    def add_a_new_habit(self, name, category, frequency):
        new_habit = [name, category, frequency]
        self.habits.append(new_habit)


    def complete(self):
        self.streak += 1
        print(f"Nice you are on a {self.streak} day streak")



# Test
kai_habits = NewHabit()
kai_habits.add_a_new_habit("Drink Water", "Health", "Daily")

print(kai_habits.habits)