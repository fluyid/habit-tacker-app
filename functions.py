import os
from fpdf import FPDF
from datetime import datetime
import json

from backend import HabitManager, Habit


def generate_habit_pdf(habit):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font(family="DejaVu", style="", fname="DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    # Title
    pdf.cell(w=200, h=10, text=f"Habit Report {habit.name}", ln=True, align="C")

    # Basic Info
    pdf.ln(h=10)
    pdf.cell(w=200, h=10, text=f"Category: {habit.category}", ln=True)
    pdf.cell(w=200, h=10, text=f"Frequency: {habit.frequency}", ln=True)

    # Stats
    stats = habit.get_stats()
    streak = habit.calculate_streak()

    pdf.ln(h=10)
    pdf.cell(w=200, h=10, text=f"Total Logs: {stats['total_entries']}", ln=True)
    pdf.cell(w=200, h=10, text=f"Current Streak: {streak} days", ln=True)

    # Log Timeline
    pdf.ln(h=10)
    pdf.cell(w=200, h=10, text="Log Timeline:", ln=True)
    pdf.ln(h=5)

    if habit.log:
        for index, entry in enumerate(habit.log, 1):
            timestamp = entry["timestamp"].strftime("%d/%m/%Y %H:%M")
            note = entry["note"]
            line = f"{index}. [{timestamp}] - {note}"
            pdf.multi_cell(w=0, h=10, text=line)
            pdf.ln(1)
    else:
        pdf.cell(w=200, h=10, text="No log entries yet", ln=True)
    return pdf.output(dest="S")


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
