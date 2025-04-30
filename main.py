import streamlit as st
from backend import HabitManager, Habit
import json
import os
from datetime import datetime


# Functions
# Saving to a json file
def save_habits(habits, filename="habits.json"):
    habits_data = []
    for habit in habits.habits:
        habits_data.append({
            "name": habit.name,
            "category": habit.category,
            "frequency": habit.frequency,
            "log": [
                {"timestamp": entry["timestamp"].isoformat(), "note": entry["note"]} for entry in habit.log
            ]
        })
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(obj=habits_data, fp=file, indent=4)


# Loading the habits from a json file
def load_habits(filename="habits.json"):
    habits = HabitManager()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            habits_data = json.load(file)
            habits.habits = []
            for habit_data in habits_data:
                habit = Habit(
                    name=habit_data["name"],
                    category=habit_data["category"],
                    frequency=habit_data["frequency"]
                )
                habit.log = [
                    {
                        "timestamp": datetime.fromisoformat(entry["timestamp"]),
                        "note": entry["note"]
                    } for entry in habit_data["log"]
                ]
                habits.habits.append(habit)
    return habits


st.title("Habit Tracker App")

# Initialising the HabitManager
if "habits" not in st.session_state:
    st.session_state.habits = load_habits()

habits = st.session_state.habits

# Sidebar
st.sidebar.header("Create a new Habit")
with st.sidebar.form(key="create_habit_form"):
    habit_name = st.text_input(label="Habit Name", placeholder="Clean the house")
    habit_category = st.radio(label="Category", options=("Health", "Productivity", "Personal Growth"))
    habit_frequency = st.radio(label="Frequency", options=("Daily", "Weekly"))
    create_button = st.form_submit_button(label="Create Habit")
    if create_button:
        habits.create_habit(name=habit_name, category=habit_category, frequency=habit_frequency)
        st.success(f"Habit '{habit_name}' created")

# Main Area
st.header("Manage Your Habits")

habit_list = habits.get_habit_names()
if habit_list:
    selected_habit_names = st.selectbox(label="Select a Habit", options=habit_list)
    selected_habit = habits.get_habit_by_name(selected_habit_names)

    st.subheader(f"Habit: {selected_habit.name}")
    st.write(f"**Category:** {selected_habit.category}")
    st.write(f"**Total Entries:** {selected_habit.get_stats()['total_entries']}")

    # Log Progress
    with st.form(key="log_form"):
        note = st.text_area(label="Log your progress")
        log_button = st.form_submit_button(label="Add Log Entry")
        if log_button:
            selected_habit.log_progress(note)
            save_habits(habits)
            st.success("Log entry added!")

    # View Habit Log
    st.subheader("Habit Log Timeline")
    logs = selected_habit.show_log()
    print("----Testing Logs")
    print(f"Selected Habit: {selected_habit.name}")
    print(logs)
    st.text_area("Timeline", logs, height=300)

    # Habit Progress Chart
    st.subheader("Habit Progress Chart")
    df = selected_habit.get_logs_as_dataframe()
    if df.empty:
        st.info("No progress entries yet to show on the chart")
    else:
        # Line chart for consistency over time
        st.line_chart(data=df.set_index("Date"))
        # Bar chart for how active I am on different days
        st.bar_chart(data=df.set_index("Date"))

    # Habit Streak
    st.subheader("Habit Streak")

    streak_count = selected_habit.calculate_streak()
    if streak_count > 0:
        st.success(f"You have a {streak_count}🔥 day streak going!")
    else:
        st.info("You currently don't have a streak :/ Let's start today!")
else:
    st.info("No habits yet. Create a new one from the sidebar!")
