#!/usr/bin/env python3
"""Tiny JSON API layer so a Swift app can talk to the habit data."""

import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from functions import DEFAULT_DATA_FILE, load_habits, save_habits

DATA_FILE = DEFAULT_DATA_FILE


def habit_to_dict(habit):
    """Convert a Habit object into clean JSON-ready data."""
    return {
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
                "note": entry.get("note", ""),
            }
            for entry in habit.log
        ],
        "stats": {
            "total_entries": habit.get_stats()["total_entries"],
            "total_value": habit.get_total_value(),
            "current_streak": habit.calculate_streak(),
            "longest_streak": habit.calculate_longest_streak(),
        },
    }


class HabitAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler with basic GET/POST endpoints for habits."""

    def _read_json(self):
        """Read request JSON safely and return an empty dict if no body."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _write_json(self, payload, status=HTTPStatus.OK):
        """Send a JSON response with the given status code."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _load_manager(self):
        """Load fresh habit data from disk for each request."""
        return load_habits(DATA_FILE)

    def log_message(self, fmt, *args):
        """Silence default request logging to keep terminal output clean."""
        return

    def do_GET(self):
        """Handle read-only routes like health, habits list, and stats."""
        manager = self._load_manager()
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            self._write_json({"status": "ok"})
            return

        if path == "/habits":
            params = parse_qs(parsed.query)
            frequency = params.get("frequency", [None])[0]
            if frequency:
                habits = manager.get_habits_by_periodicity(frequency)
            else:
                habits = manager.habits
            self._write_json({"habits": [habit_to_dict(habit) for habit in habits]})
            return

        if path.startswith("/habits/"):
            name = unquote(path.split("/", 2)[2])
            habit = manager.get_habit_by_name(name)
            if not habit:
                self._write_json({"error": "Habit not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._write_json({"habit": habit_to_dict(habit)})
            return

        if path == "/stats/longest-streak":
            self._write_json({"longest_run_streak": manager.get_longest_run_streak()})
            return

        self._write_json({"error": "Route not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self):
        """Handle create routes for habits and new log entries."""
        manager = self._load_manager()
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/habits":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._write_json({"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
                return

            name = str(payload.get("name", "")).strip()
            category = str(payload.get("category", "")).strip()
            frequency = str(payload.get("frequency", "")).strip().title()
            tracking_type = str(payload.get("tracking_type", "numeric")).strip().lower()
            unit = str(payload.get("unit", "count")).strip()
            if tracking_type == "boolean":
                unit = "completion"

            if not name or not category or not unit or frequency not in {"Daily", "Weekly"}:
                self._write_json(
                    {"error": "name, category, unit, and frequency (Daily/Weekly) are required"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if tracking_type not in {"numeric", "boolean"}:
                self._write_json({"error": "tracking_type must be numeric or boolean"}, status=HTTPStatus.BAD_REQUEST)
                return

            if manager.get_habit_by_name(name):
                self._write_json({"error": "Habit already exists"}, status=HTTPStatus.CONFLICT)
                return

            habit = manager.create_habit(name, category, frequency, unit, tracking_type)
            save_habits(manager, DATA_FILE)
            self._write_json({"habit": habit_to_dict(habit)}, status=HTTPStatus.CREATED)
            return

        if path.startswith("/habits/") and path.endswith("/logs"):
            # /habits/{name}/logs
            name = unquote(path[len("/habits/") : -len("/logs")]).rstrip("/")
            habit = manager.get_habit_by_name(name)
            if not habit:
                self._write_json({"error": "Habit not found"}, status=HTTPStatus.NOT_FOUND)
                return

            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._write_json({"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
                return

            note = str(payload.get("note", "")).strip()
            if habit.tracking_type == "boolean":
                completed = payload.get("completed")
                if not isinstance(completed, bool):
                    self._write_json({"error": "completed must be true or false"}, status=HTTPStatus.BAD_REQUEST)
                    return
                habit.log_progress(completed=completed, note=note)
            else:
                try:
                    value = float(payload.get("value", 0))
                except (TypeError, ValueError):
                    self._write_json({"error": "value must be a number"}, status=HTTPStatus.BAD_REQUEST)
                    return

                if value <= 0:
                    self._write_json({"error": "value must be greater than 0"}, status=HTTPStatus.BAD_REQUEST)
                    return
                habit.log_progress(value=value, note=note)

            save_habits(manager, DATA_FILE)
            self._write_json({"habit": habit_to_dict(habit)}, status=HTTPStatus.CREATED)
            return

        self._write_json({"error": "Route not found"}, status=HTTPStatus.NOT_FOUND)


def run(host="127.0.0.1", port=8080):
    """Start the API server and keep it running."""
    server = ThreadingHTTPServer((host, port), HabitAPIHandler)
    print(f"Habit API listening at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
