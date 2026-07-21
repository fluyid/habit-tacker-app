# Habit Tracker App

A Streamlit habit tracker where you can create habits, log progress, track streaks, and export PDF reports.

> Portfolio project for **Object Oriented and Functional Programming with Python (DLBDSOOFPP01)**,
> IU International University of Applied Sciences.

---

## Features

- **Create habits** with a name, category, frequency (`Daily` / `Weekly`) and tracking type:
  - **Numeric** — unit-based (`km`, `minutes`, `reps`, `ml`, `pages`, or a custom unit)
  - **Yes/No** — completion-style habits like "Clean the house"
- **Edit** any habit from a single `Edit Habit` button (name, category, frequency, tracking type, unit)
- **Delete** habits you no longer track
- **Log entries** with an optional note — a value for numeric habits, Yes/No for completion habits
- **Reminders** — habits with no entry in the current period are flagged
- **Analytics** — currently tracked habits, habits by periodicity, longest streak overall,
  longest streak for a single habit
- **Filter** habits by frequency
- **Export** a per-habit PDF report
- **Persist** all data in JSON between sessions

---

## Requirements

- **Python 3.10 or newer** (developed and tested on 3.13)
- macOS, Linux, or Windows

---

## Setup

1. Clone or download this repository.
2. Open a terminal in the project root (the folder containing `main.py`).
3. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate` instead.

4. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

> Using `python -m pip` rather than `pip` guarantees you install into the active virtual
> environment, even if another Python (Homebrew, conda) is earlier on your `PATH`.

---

## Run the app

### Quick way

```bash
./scripts/open_app.sh
```

Starts the app and opens your browser automatically.

### Manual way

```bash
streamlit run main.py --server.address 127.0.0.1 --server.port 8501
```

Then open `http://localhost:8501`.

Run from the project root — the PDF export loads `DejaVuSans.ttf` from there.

---

## Using the app

### Create a habit

1. Open the sidebar on the left.
2. Enter a **Habit Name**, e.g. `Drink water`.
3. Choose a **Category**.
4. Choose a **Frequency**:
   - **Daily** — must be completed at least once each day
   - **Weekly** — must be completed at least once each calendar week (Monday–Sunday)
5. Choose an **Entry Type**:
   - **Numeric** — you record an amount, e.g. `2000 ml`. Pick a unit, or choose
     `other` to type your own.
   - **Yes/No** — you record only whether you did it.
6. Click **Create Habit**.

The habit is saved to `data/habits.json` straight away, so it survives a restart.

### Complete a task within the current period

1. Find the habit in the main area and expand its panel.
2. For **numeric** habits, enter the value you achieved and an optional note.
3. For **Yes/No** habits, choose `Yes` or `No` and an optional note.
4. Click **Log**.

The entry is timestamped at the moment you log it, and the streak recalculates immediately.

A habit is tagged **🟨 Update required** when the current period has no entry yet —
today for daily habits, this week for weekly habits. Weekly reminders appear only in the
final 48 hours of the week, so they nudge you rather than nag you.

### Edit a habit

Expand the habit, click **Edit Habit**, change any field, and save. Existing log entries
are converted to match if you switch tracking type.

### Delete a habit

Expand the habit and click **Delete Habit**. This removes the habit and its full log.

### Export a report

Expand the habit and click **Download PDF Report** for a one-page summary: definition,
totals, current streak, and the full log timeline.

---

## Predefined habits and example data

The app ships with **5 predefined habits** and **4 weeks of example tracking data** in
`data/habits.json`. The example data acts as the test fixture and gives you something to
explore before recording anything of your own.

| Habit | Frequency | Tracking type | Unit |
|---|---|---|---|
| Workout | Daily | Numeric | reps |
| Read a book | Daily | Numeric | pages |
| Meditate | Daily | Numeric | minutes |
| Clean the house | Weekly | Yes/No | completion |
| Grocery Shopping | Weekly | Yes/No | completion |

The example data deliberately includes both unbroken runs and broken streaks, so the
streak calculations can be verified against known expected values.

To start from a blank slate, delete `data/habits.json` and restart the app — the five
predefined habits are recreated with empty logs.

---

## Analytics

Analytics are exposed as **pure functions** in `analytics.py`. Each takes habit data as
an argument and returns a result without changing anything:

```python
from functions import load_habits
import analytics

manager = load_habits()
habits = manager.habits

analytics.get_tracked_habits(habits)                    # names of all tracked habits
analytics.get_habits_by_periodicity(habits, "Daily")    # only the daily habits
analytics.get_longest_streak_all(habits)                # best streak across every habit
analytics.get_longest_streak_for(habits, "Workout")     # best streak for one habit
```

<!-- TODO: confirm these names match analytics.py once it is written -->

The same functions back the metrics shown in the user interface, so the numbers on screen
and the numbers in code are always the same numbers.

---

## Architecture

The project deliberately separates two programming paradigms.

### Object-oriented — `backend.py`

Models the domain, where state genuinely belongs to a thing.

- **`Habit`** — a single habit: its definition (name, category, frequency, tracking type,
  unit), its log of entries, and the streak logic that depends on them.
- **`HabitManager`** — owns the collection of habits: create, update, delete, look up.

### Functional — `analytics.py`

Analyses the data, where nothing needs to be owned.

Pure functions that receive habit data as an argument and return a result. They hold no
state, mutate nothing, and are built from `filter`, `map`, `reduce` and comprehensions.
Given the same input they always produce the same output, which makes them simple to test
and safe to compose.

### Supporting modules

| File | Responsibility |
|---|---|
| `main.py` | Streamlit user interface |
| `functions.py` | JSON persistence and PDF report generation |
| `tests/` | Unit tests for the models, analytics, and persistence |
| `data/habits.json` | Persisted habit data and example fixture |
| `DejaVuSans.ttf` | Unicode font used by the PDF export |
| `requirements.txt` | Pinned dependencies |
| `scripts/open_app.sh` | Launch helper that also opens the browser |

---

## Run tests

```bash
python -m unittest discover -s tests -v
```

or, equivalently:

```bash
python -m pytest -v
```

The suite covers habit creation and logging, daily and weekly streak calculation,
the analytics functions, reminder logic, JSON round-trips, and PDF generation.

---

## Data format

Data is stored as a JSON list in `data/habits.json`. One habit looks like this:

```json
{
  "name": "Workout",
  "category": "Health",
  "frequency": "Daily",
  "tracking_type": "numeric",
  "unit": "reps",
  "log": [
    {
      "timestamp": "2026-02-08T12:00:00",
      "value": 30.0,
      "completed": null,
      "unit": "reps",
      "note": "morning session"
    }
  ]
}
```

- **Numeric habits** store the amount in `value`, and `completed` is `null`.
- **Yes/No habits** store `true` / `false` in `completed`, with `value` mirroring it
  as `1.0` / `0.0` so both kinds of habit can share the same charting code.

Older log formats are upgraded automatically when loaded.

---

## Roadmap

- HTTP API layer for a future native mobile client (early prototype, not part of this release)
