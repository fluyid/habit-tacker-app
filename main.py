"""Streamlit UI for creating, editing, and tracking habits with units."""

import base64
import streamlit as st
from functions import generate_habit_pdf, save_habits, load_habits

st.title("Habit Tracker App")
UNIT_OPTIONS = ("km", "minutes", "count", "reps", "ml", "pages", "other")
CATEGORY_OPTIONS = ("Health", "Productivity", "Personal Growth", "Growth")
FREQUENCY_OPTIONS = ("Daily", "Weekly")
TRACKING_TYPE_OPTIONS = ("numeric", "boolean")

# Initialising the HabitManager
if "habits" not in st.session_state:
    st.session_state.habits = load_habits()

habits = st.session_state.habits

# Sidebar
st.sidebar.header("Create a new Habit")
with st.sidebar.form(key="create_habit_form"):
    habit_name = st.text_input(label="Habit Name", placeholder="Clean the house (required)")
    habit_category = st.radio(label="Category", options=CATEGORY_OPTIONS)
    habit_frequency = st.radio(label="Frequency", options=FREQUENCY_OPTIONS)
    habit_tracking_type = st.radio("Entry Type", options=TRACKING_TYPE_OPTIONS, format_func=lambda x: "Numeric" if x == "numeric" else "Yes/No")
    habit_unit_choice = "count"
    habit_custom_unit = ""
    if habit_tracking_type == "numeric":
        habit_unit_choice = st.selectbox("Unit", options=UNIT_OPTIONS)
        if habit_unit_choice == "other":
            habit_custom_unit = st.text_input(label="Custom Unit", placeholder="e.g. laps")
    create_button = st.form_submit_button(label="Create Habit")
    if create_button:
        name = habit_name.strip()
        if habit_tracking_type == "boolean":
            unit = "completion"
        else:
            unit = habit_custom_unit.strip() if habit_unit_choice == "other" else habit_unit_choice
        if not name:
            st.error("Habit name is required.")
        elif not unit:
            st.error("Please choose or enter a valid unit.")
        elif habits.get_habit_by_name(name):
            st.error(f"Habit '{name}' already exists.")
        else:
            habits.create_habit(
                name=name,
                category=habit_category,
                frequency=habit_frequency,
                unit=unit,
                tracking_type=habit_tracking_type
            )
            save_habits(habits)
            st.success(f"Habit '{name}' created")

# Main Area
st.header("Manage Your Habits")
periodicity_choice = st.selectbox("Filter habits by periodicity", options=("Daily", "Weekly"))
matching_habits = habits.get_habits_by_periodicity(periodicity_choice)
if matching_habits:
    st.caption(f"{periodicity_choice} habits: {', '.join(habit.name for habit in matching_habits)}")
else:
    st.caption(f"No {periodicity_choice.lower()} habits found.")
st.metric(label="Longest Run Streak Across All Habits", value=habits.get_longest_run_streak())

if habits.habits:
    for idx, habit in enumerate(habits.habits):
        reminder_tag = "  🟨 Update required" if habit.needs_update() else ""
        with st.expander(f"🔷 {habit.name}{reminder_tag}"):
            # Habit Info
            st.write(f"**Category:** {habit.category}")
            st.write(f"**Frequency:** {habit.frequency.capitalize()}")
            st.write(f"**Entry Type:** {'Yes/No' if habit.tracking_type == 'boolean' else 'Numeric'}")
            if habit.tracking_type == "numeric":
                st.write(f"**Unit:** {habit.unit}")
            stats = habit.get_stats()
            streak = habit.calculate_streak()

            edit_state_key = f"show_edit_{idx}"
            if edit_state_key not in st.session_state:
                st.session_state[edit_state_key] = False

            if st.button("Edit Habit", key=f"toggle_edit_{idx}"):
                st.session_state[edit_state_key] = not st.session_state[edit_state_key]

            delete_state_key = f"confirm_delete_{idx}"
            if delete_state_key not in st.session_state:
                st.session_state[delete_state_key] = False

            if st.button("Delete Habit", key=f"toggle_delete_{idx}"):
                st.session_state[delete_state_key] = True

            if st.session_state[delete_state_key]:
                st.warning(f"Delete '{habit.name}' and all its logs? This cannot be undone.")
                confirm_col, cancel_col = st.columns(2)
                if confirm_col.button("Yes, delete", key=f"confirm_delete_btn_{idx}"):
                    success, message = habits.delete_habit(habit.name)
                    if success:
                        save_habits(habits)
                        st.session_state[delete_state_key] = False
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                if cancel_col.button("Cancel", key=f"cancel_delete_btn_{idx}"):
                    st.session_state[delete_state_key] = False
                    st.rerun()

            if st.session_state[edit_state_key]:
                current_category = habit.category if habit.category in CATEGORY_OPTIONS else CATEGORY_OPTIONS[0]
                current_frequency = habit.frequency if habit.frequency in FREQUENCY_OPTIONS else FREQUENCY_OPTIONS[0]
                current_tracking_type = habit.tracking_type if habit.tracking_type in TRACKING_TYPE_OPTIONS else "numeric"
                current_unit = habit.unit.strip()
                default_unit_choice = current_unit if current_unit in UNIT_OPTIONS[:-1] else "other"

                with st.form(key=f"edit_form_{idx}"):
                    edit_name = st.text_input("Habit Name", value=habit.name, key=f"edit_name_{idx}")
                    edit_category = st.selectbox(
                        "Category",
                        options=CATEGORY_OPTIONS,
                        index=CATEGORY_OPTIONS.index(current_category),
                        key=f"edit_category_{idx}"
                    )
                    edit_frequency = st.selectbox(
                        "Frequency",
                        options=FREQUENCY_OPTIONS,
                        index=FREQUENCY_OPTIONS.index(current_frequency),
                        key=f"edit_frequency_{idx}"
                    )
                    edit_tracking_type = st.selectbox(
                        "Entry Type",
                        options=TRACKING_TYPE_OPTIONS,
                        index=TRACKING_TYPE_OPTIONS.index(current_tracking_type),
                        format_func=lambda x: "Numeric" if x == "numeric" else "Yes/No",
                        key=f"edit_tracking_type_{idx}"
                    )
                    edit_unit_choice = "count"
                    edit_custom_unit = ""
                    if edit_tracking_type == "numeric":
                        edit_unit_choice = st.selectbox(
                            "Unit",
                            options=UNIT_OPTIONS,
                            index=UNIT_OPTIONS.index(default_unit_choice),
                            key=f"edit_unit_choice_{idx}"
                        )
                        if edit_unit_choice == "other":
                            edit_custom_unit = st.text_input(
                                "Custom Unit",
                                value=current_unit if default_unit_choice == "other" else "",
                                key=f"edit_custom_unit_{idx}"
                            )

                    save_edit = st.form_submit_button("Save Habit Changes")
                    cancel_edit = st.form_submit_button("Cancel")

                    if save_edit:
                        if edit_tracking_type == "boolean":
                            updated_unit = "completion"
                        else:
                            updated_unit = edit_custom_unit.strip() if edit_unit_choice == "other" else edit_unit_choice
                        ok, message = habits.update_habit(
                            current_name=habit.name,
                            new_name=edit_name,
                            category=edit_category,
                            frequency=edit_frequency,
                            unit=updated_unit,
                            tracking_type=edit_tracking_type
                        )
                        if ok:
                            save_habits(habits)
                            st.session_state[edit_state_key] = False
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

                    if cancel_edit:
                        st.session_state[edit_state_key] = False
                        st.rerun()

            # Log Form
            with st.form(key=f"log_form_{habit.name}"):
                if habit.tracking_type == "boolean":
                    completed_choice = st.radio(
                        "Completed?",
                        options=("Yes", "No"),
                        key=f"completed_{habit.name}",
                        horizontal=True
                    )
                    log_value = None
                else:
                    log_value = st.number_input(
                        f"Enter progress ({habit.unit})",
                        min_value=0.0,
                        step=1.0,
                        key=f"value_{habit.name}"
                    )
                    completed_choice = None
                log_note = st.text_input("Optional note", key=f"note_{habit.name}").strip()
                submit_button = st.form_submit_button("Log Progress")
                if submit_button:
                    if habit.tracking_type == "boolean":
                        habit.log_progress(completed=(completed_choice == "Yes"), note=log_note)
                        save_habits(habits)
                        st.success(f"Logged completion: {completed_choice}")
                        st.rerun()
                    elif log_value > 0:
                        habit.log_progress(value=log_value, note=log_note)
                        save_habits(habits)
                        st.success(f"Logged {log_value} {habit.unit} successfully!")
                        st.rerun()
                    else:
                        st.error("Progress value must be greater than 0.")

            # Key stats
            st.metric(label="Total Logs", value=stats["total_entries"])
            if habit.tracking_type == "boolean":
                completion_counts = habit.get_completion_counts()
                st.metric(label="Yes Count", value=completion_counts["yes"])
                st.metric(label="No Count", value=completion_counts["no"])
            else:
                st.metric(label=f"Total {habit.unit}", value=habit.get_total_value())
            streak_unit = "times" if habit.frequency == "Weekly" else "days"
            st.metric(label="Current Streak", value=f"{streak} {streak_unit}")

            # Mini progress graph
            df = habit.get_logs_as_dataframe()
            if not df.empty:
                st.line_chart(df.set_index("Date"))
            else:
                st.info("No logs yet")

            # Longest Streak
            longest_streak = habit.calculate_longest_streak()
            st.metric(label="Longest Streak", value=f"{longest_streak} {habit.frequency.lower()} entries")

            # Download PDF report
            pdf_data = generate_habit_pdf(habit)
            b64 = base64.b64encode(pdf_data).decode()
            href = (f"<a href='data:application/octet-steam;base64,{b64}' download='{habit.name}_report.pdf'> Download "
                    f"Habit Report (PDF)</a>")
            st.markdown(href, unsafe_allow_html=True)
else:
    st.info("No habits yet. Create a new one from the sidebar!")
