#!/usr/bin/env python3
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from functions import load_habits, save_habits

DATA_FILE = "habits.json"


def habit_to_dict(habit):
    return {
        "name": habit.name,
        "category": habit.category,
        "frequency": habit.frequency,
        "log": [
            {
                "timestamp": entry["timestamp"].isoformat(),
                "note": entry["note"],
            }
            for entry in habit.log
        ],
        "stats": {
            "total_entries": habit.get_stats()["total_entries"],
            "current_streak": habit.calculate_streak(),
            "longest_streak": habit.calculate_longest_streak(),
        },
    }


class HabitAPIHandler(BaseHTTPRequestHandler):
    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _write_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _load_manager(self):
        return load_habits(DATA_FILE)

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
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

            if not name or not category or frequency not in {"Daily", "Weekly"}:
                self._write_json(
                    {"error": "name, category, and frequency (Daily/Weekly) are required"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            if manager.get_habit_by_name(name):
                self._write_json({"error": "Habit already exists"}, status=HTTPStatus.CONFLICT)
                return

            habit = manager.create_habit(name, category, frequency)
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
            if not note:
                self._write_json({"error": "note is required"}, status=HTTPStatus.BAD_REQUEST)
                return

            habit.log_progress(note)
            save_habits(manager, DATA_FILE)
            self._write_json({"habit": habit_to_dict(habit)}, status=HTTPStatus.CREATED)
            return

        self._write_json({"error": "Route not found"}, status=HTTPStatus.NOT_FOUND)


def run(host="127.0.0.1", port=8080):
    server = ThreadingHTTPServer((host, port), HabitAPIHandler)
    print(f"Habit API listening at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
