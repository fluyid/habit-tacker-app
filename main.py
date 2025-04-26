import streamlit as st
from backend import HabitManager

st.title("Habit Tracker App")

# Initialising the HabitManager
if "habits" not in st.session_state:
    st.session_state.habits = HabitManager()

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
            st.success("Log entry added!")

    # View Habit Log
    st.subheader("Habit Log Timeline")
    logs = selected_habit.show_log()
    st.text_area(label="Timeline", value=logs, height=300)
else:
    st.info("No habits yet. Create a new one from the sidebar!")
