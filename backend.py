# Creating a Habit instance
# Create User
# Create Habits class
# Create classes for different kinds of habits - Health, Productivity, Learning and Growth, Financial Habits,
# social and relationship habits, spiritual and mindfulness, create habits



class Habit:
    def __init__(self, name, category, frequency):
        self.name = name
        self.category = category
        self.frequency = frequency
        self.streak = 0

    def complete(self):
        self.streak += 1
        print(f"Nice you are on a {self.streak} day streak")



