import base64

import streamlit as st
from backend import HabitManager, Habit
import json
import os
from datetime import datetime
from functions import generate_habit_pdf, save_habits, load_habits

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
        save_habits(habits)
        st.success(f"Habit '{habit_name}' created")

# Main Area
st.header("Manage Your Habits")

# habit_list = habits.get_habit_names()
# if habit_list:
#     selected_habit_names = st.selectbox(label="Select a Habit", options=habit_list)
#     selected_habit = habits.get_habit_by_name(selected_habit_names)
#
#     st.subheader(f"Habit: {selected_habit.name}")
#     st.write(f"**Category:** {selected_habit.category}")
#     st.write(f"**Total Entries:** {selected_habit.get_stats()['total_entries']}")
#
#     # Log Progress
#     with st.form(key="log_form"):
#         note = st.text_area(label="Log your progress")
#         log_button = st.form_submit_button(label="Add Log Entry")
#         if log_button:
#             selected_habit.log_progress(note)
#             save_habits(habits)
#             st.success("Log entry added!")
#
#     # View Habit Log
#     st.subheader("Habit Log Timeline")
#     logs = selected_habit.show_log()
#     print("----Testing Logs")
#     print(f"Selected Habit: {selected_habit.name}")
#     print(logs)
#     st.text_area("Timeline", logs, height=300)
#
#     # Habit Progress Chart
#     st.subheader("Habit Progress Chart")
#     df = selected_habit.get_logs_as_dataframe()
#     if df.empty:
#         st.info("No progress entries yet to show on the chart")
#     else:
#         # Line chart for consistency over time
#         st.line_chart(data=df.set_index("Date"))
#         # Bar chart for how active I am on different days
#         st.bar_chart(data=df.set_index("Date"))
#
#     # Habit Streak
#     st.subheader("Habit Streak")
#
#     streak_count = selected_habit.calculate_streak()
#     if streak_count > 0:
#         st.success(f"You have a {streak_count}🔥 day streak going!")
#     else:
#         st.info("You currently don't have a streak :/ Let's start today!")
# else:
#     st.info("No habits yet. Create a new one from the sidebar!")

if habits.habits:
    for habit in habits.habits:
        with st.expander(f"🔷 {habit.name}"):
            # Habit Info
            st.write(f"**Category:** {habit.category}")
            st.write(f"**Frequency:** {habit.frequency.capitalize()}")
            stats = habit.get_stats()
            streak = habit.calculate_streak()

            # Log Form
            with st.form(key=f"log_form_{habit.name}"):
                log_note = st.text_input("Log your progress: ", key=f"note_{habit.name}").strip()
                submit_button = st.form_submit_button("Log Progress")
                if submit_button and log_note:
                    habit.log_progress(log_note)
                    save_habits(habits)
                    st.success("Progress logged successfully!")
                    st.rerun()

            # Key stats
            st.metric(label="Total Logs", value=stats["total_entries"])
            st.metric(label="Current Streak", value=f"{streak} days")

            # Mini progress graph
            df = habit.get_logs_as_dataframe()
            if not df.empty:
                st.line_chart(df.set_index("Date"))
            else:
                st.info("No logs yet")

            # Download PDF report
            pdf_data = generate_habit_pdf(habit)
            b64 = base64.b64encode(pdf_data).decode()
            href = (f"<a href='data:application/octet-steam;base64,{b64}' download='{habit.name}_report.pdf'> Download "
                    f"Habit Report (PDF)</a>")
            st.markdown(href, unsafe_allow_html=True)
else:
    st.info("No habits yet. Create a new one from the sidebar!")
