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

