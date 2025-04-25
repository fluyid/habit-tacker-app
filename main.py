import streamlit as st
from backend import Habit, NewHabit

# def start_page():
#     st.subheader("What would you like to do today")
#     action = st.selectbox("Select an action",
#                           ("log for an existing habit", "Add a new habit", "Analyse current habits"), key=1)
#     return action

def create_habit(name, frequency, category):
    kai_habits.add_a_new_habit(name, frequency, category)
    # st.rerun()
    # start_page()


st.title("Habit Tracker App")
st.subheader("Hello Kai")

st.subheader("What would you like to do today")
action = st.selectbox("Select an action",
                      ("log for an existing habit", "Add a new habit", "Analyse current habits"), key="action")

match action:
    case "Add a new habit":
        name_of_habit = st.text_input("Enter a new habit: ")
        frequency_of_habit = st.radio("How often would you like to do this?", ("Daily", "Weekly"))
        category_of_habit = st.selectbox("What category would this habit fall under?", ("Health", "Productivity",
                                                                                        "Learning and Growth"),
                                         key="category")
        kai_habits = NewHabit()
        st.button(label="Create Habit",
                  on_click=create_habit(name_of_habit, frequency_of_habit, category_of_habit), key="create habit")



