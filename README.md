# Habit Tracker App

A Streamlit habit tracker where you can create habits, log progress, track streaks, and export PDF reports.

## Features

- Create habits with:
  - name
  - category
  - frequency (`Daily` / `Weekly`)
  - tracking type:
    - `Numeric` (unit-based: `km`, `minutes`, `reps`, `ml`, custom)
    - `Yes/No` (completion-style habits like "Clean the house")
- Edit a habit from one place (single `Edit Habit` button):
  - name
  - category
  - frequency
  - tracking type
  - unit
- Log entries:
  - numeric value + optional note for numeric habits
  - `Yes`/`No` + optional note for boolean habits
- Metrics:
  - total logs
  - total value (numeric habits)
  - yes/no counts (boolean habits)
  - current streak and longest streak
  - longest streak across all habits
- Filter habits by frequency
- Export per-habit PDF report
- Persist data in JSON

## Project structure

- `main.py`: Streamlit UI
- `backend.py`: core models + streak logic + manager ops
- `functions.py`: JSON persistence + PDF generation
- `scripts/swift_backend.py`: lightweight HTTP API (**Work in Progress**)
- `scripts/open_app.sh`: launch script that also opens browser
- `tests/`: unit tests
- `data/habits.json`: persisted app data

## Setup

1. Clone/download this repo.
2. Open a terminal in the project root (the folder containing `main.py`).
3. (Recommended) Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the app

### Quick way

```bash
./scripts/open_app.sh
```

### Manual way

```bash
streamlit run main.py --server.address 127.0.0.1 --server.port 8501
```

Open: `http://localhost:8501`

## Run tests

```bash
python -m unittest discover -s tests -v
```

## API (Work in Progress)

`scripts/swift_backend.py` is currently an early integration layer for mobile/Swift work.

Start it with:

```bash
python scripts/swift_backend.py
```

Default URL: `http://127.0.0.1:8080`

Current routes:

- `GET /health`
- `GET /habits`
- `GET /habits?frequency=Daily`
- `GET /habits/{name}`
- `GET /stats/longest-streak`
- `POST /habits`
- `POST /habits/{name}/logs`

### API examples

Create numeric habit:

```bash
curl -X POST http://127.0.0.1:8080/habits \
  -H 'Content-Type: application/json' \
  -d '{"name":"Run","category":"Health","frequency":"Daily","tracking_type":"numeric","unit":"km"}'
```

Create yes/no habit:

```bash
curl -X POST http://127.0.0.1:8080/habits \
  -H 'Content-Type: application/json' \
  -d '{"name":"Clean the house","category":"Productivity","frequency":"Weekly","tracking_type":"boolean"}'
```

Log numeric progress:

```bash
curl -X POST http://127.0.0.1:8080/habits/Run/logs \
  -H 'Content-Type: application/json' \
  -d '{"value":5.2,"note":"easy pace"}'
```

Log yes/no progress:

```bash
curl -X POST http://127.0.0.1:8080/habits/Clean%20the%20house/logs \
  -H 'Content-Type: application/json' \
  -d '{"completed":true,"note":"done before lunch"}'
```

## Data format

Data is stored in `data/habits.json`.

Example shape:

```json
{
  "name": "Run",
  "category": "Health",
  "frequency": "Daily",
  "tracking_type": "numeric",
  "unit": "km",
  "log": [
    {
      "timestamp": "2026-02-08T12:00:00",
      "value": 5.2,
      "completed": null,
      "unit": "km",
      "note": "easy pace"
    }
  ]
}
```

For boolean habits, `value` is `1.0` (Yes) or `0.0` (No), and `completed` is `true`/`false`.

## Notes

- Older JSON formats are auto-upgraded when loading.
- PDF export needs `fpdf2`; if missing, the rest of the app still runs.
