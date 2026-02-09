import os
from datetime import datetime
import json
from backend import HabitManager, Habit

DATA_DIR = "data"
DEFAULT_DATA_FILE = os.path.join(DATA_DIR, "habits.json")


def generate_habit_pdf(habit):
    """Build a simple PDF report for one habit and return it as bytes."""
    from fpdf import FPDF

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
    pdf.cell(w=200, h=10, text=f"Tracking Type: {habit.tracking_type}", ln=True)
    pdf.cell(w=200, h=10, text=f"Unit: {habit.unit}", ln=True)

    # Stats
    stats = habit.get_stats()
    streak = habit.calculate_streak()

    pdf.ln(h=10)
    pdf.cell(w=200, h=10, text=f"Total Logs: {stats['total_entries']}", ln=True)
    if habit.tracking_type == "boolean":
        counts = habit.get_completion_counts()
        pdf.cell(w=200, h=10, text=f"Yes: {counts['yes']} | No: {counts['no']}", ln=True)
    else:
        pdf.cell(w=200, h=10, text=f"Total {habit.unit}: {habit.get_total_value()}", ln=True)
    pdf.cell(w=200, h=10, text=f"Current Streak: {streak} days", ln=True)

    # Log Timeline
    pdf.ln(h=10)
    pdf.cell(w=200, h=10, text="Log Timeline:", ln=True)
    pdf.ln(h=5)

    if habit.log:
        for index, entry in enumerate(habit.log, 1):
            timestamp = entry["timestamp"].strftime("%d/%m/%Y %H:%M")
            note = entry.get("note", "")
            note_part = f" ({note})" if note else ""
            if habit.tracking_type == "boolean":
                status = "Yes" if entry.get("completed") else "No"
                line = f"{index}. [{timestamp}] - Completed: {status}{note_part}"
            else:
                value = entry.get("value", 0.0)
                unit = entry.get("unit", habit.unit)
                line = f"{index}. [{timestamp}] - {value} {unit}{note_part}"
            pdf.multi_cell(w=0, h=10, text=line)
            pdf.ln(1)
    else:
        pdf.cell(w=200, h=10, text="No log entries yet", ln=True)
    return pdf.output(dest="S")


def save_habits(habits, filename=DEFAULT_DATA_FILE):
    """Save all habits to JSON so the app can pick up where you left off."""
    parent_dir = os.path.dirname(filename)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    habits_data = []
    for habit in habits.habits:
        habits_data.append({
            "name": habit.name,
            "category": habit.category,
            "frequency": habit.frequency,
            "tracking_type": habit.tracking_type,
            "unit": habit.unit,
            "log": [
                {
                    "timestamp": entry["timestamp"].isoformat(),
                    "value": float(entry.get("value", 0.0)),
                    "completed": entry.get("completed"),
                    "unit": entry.get("unit", habit.unit),
                    "note": entry.get("note", "")
                } for entry in habit.log
            ]
        })
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(obj=habits_data, fp=file, indent=4)


def load_habits(filename=DEFAULT_DATA_FILE):
    """Load habits from JSON. Older log formats are upgraded on the fly."""
    habits = HabitManager()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            habits_data = json.load(file)
            habits.habits = []
            for habit_data in habits_data:
                habit = Habit(
                    name=habit_data["name"],
                    category=habit_data["category"],
                    frequency=habit_data["frequency"],
                    unit=habit_data.get("unit", "count"),
                    tracking_type=habit_data.get("tracking_type", "numeric")
                )
                habit.log = [
                    {
                        "timestamp": datetime.fromisoformat(entry["timestamp"]),
                        "value": float(entry.get("value", 1.0)),
                        "completed": entry.get("completed"),
                        "unit": entry.get("unit", habit.unit),
                        "note": entry.get("note", "")
                    } for entry in habit_data["log"]
                ]
                # Compatibility pass for older JSON versions.
                for entry in habit.log:
                    if habit.tracking_type == "boolean":
                        habit.unit = "completion"
                        completed = entry.get("completed")
                        if completed is None:
                            completed = float(entry.get("value", 0.0)) > 0
                        entry["completed"] = bool(completed)
                        entry["value"] = 1.0 if entry["completed"] else 0.0
                        entry["unit"] = "completion"
                    else:
                        entry["completed"] = None
                habits.habits.append(habit)
    return habits
