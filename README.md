# Habit Tracker App

A Streamlit-based habit tracker where you can:
- create habits with custom units (`km`, `minutes`, `reps`, `ml`, etc.)
- log numeric progress over time
- track streaks and totals
- edit habit settings from one place
- export a PDF report

It also includes a small JSON API (`swift_backend.py`) so a Swift app can reuse the same data.

## What the app does

- Habit creation with:
  - name
  - category
  - frequency (`Daily` or `Weekly`)
  - unit (preset or custom)
- Habit editing from one `Edit Habit` button per habit:
  - name
  - category
  - frequency
  - unit
- Progress logging:
  - numeric value tied to the habit unit
  - optional note
- Analytics:
  - current streak
  - longest streak
  - total logged value per habit
  - longest streak across all habits
  - frequency filter (daily/weekly)
- PDF export per habit
- JSON persistence in `habits.json`

## Tech stack

- Python 3
- Streamlit
- Pandas
- fpdf2 (for PDF export)
- Built-in `http.server` for API mode

## Project structure

- `main.py`: Streamlit frontend
- `backend.py`: core habit models, streak logic, and manager operations
- `functions.py`: JSON save/load + PDF generation
- `swift_backend.py`: lightweight REST-like API for mobile integration
- `open_app.sh`: one-command launcher that opens the browser
- `tests/`: unit tests
- `habits.json`: persisted app data

## Setup

From the project root:

```bash
cd /Users/kailashnah/PycharmProjects/habit-tacker-app
```

If you already have the provided virtualenv (`.venv`), activate it:

```bash
source .venv/bin/activate
```

If you need dependencies in a fresh env:

```bash
pip install streamlit pandas fpdf2
```

## Run the app

### Fastest way (recommended)

```bash
./open_app.sh
```

This starts Streamlit and opens `http://localhost:8501` in your browser.

### Manual way

```bash
streamlit run main.py --server.address 127.0.0.1 --server.port 8501
```

## Optional auth

If you want a simple password gate in the sidebar:

```bash
export HABIT_APP_PASSWORD='your-password'
./open_app.sh
```

If `HABIT_APP_PASSWORD` is not set, auth is skipped.

## Run tests

With the project virtualenv:

```bash
./.venv/bin/python -m unittest discover -s tests -v
```

## API mode (for Swift/mobile)

Start API server:

```bash
./.venv/bin/python swift_backend.py
```

Default URL: `http://127.0.0.1:8080`

### Endpoints

- `GET /health`
- `GET /habits`
- `GET /habits?frequency=Daily`
- `GET /habits/{name}`
- `GET /stats/longest-streak`
- `POST /habits`
- `POST /habits/{name}/logs`

### Example requests

Create habit:

```bash
curl -X POST http://127.0.0.1:8080/habits \
  -H 'Content-Type: application/json' \
  -d '{"name":"Run","category":"Health","frequency":"Daily","unit":"km"}'
```

Log progress:

```bash
curl -X POST http://127.0.0.1:8080/habits/Run/logs \
  -H 'Content-Type: application/json' \
  -d '{"value":5.2,"note":"easy pace"}'
```

## Data format (`habits.json`)

Each habit includes `unit`, and each log entry stores numeric `value`:

```json
{
  "name": "Run",
  "category": "Health",
  "frequency": "Daily",
  "unit": "km",
  "log": [
    {
      "timestamp": "2026-02-08T12:00:00",
      "value": 5.2,
      "unit": "km",
      "note": "easy pace"
    }
  ]
}
```

## Notes

- Older JSON entries are handled with backward compatibility when loading.
- PDF export depends on `fpdf2`; if missing, the rest of the app still works.
