from datetime import datetime
import csv
import os
import pathlib

from utils import parse_date_string, format_date


class StatsFile:
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        os.makedirs(self.filename.parent, exist_ok=True)
        self.data = None

    def read(self, begin):
        self.data = read(self.filename)
        return self.data

    def missing_days(self, dates):
        return missing_days(self.data, dates)

    def write(self, data):
        store(self.filename, self.data, data)


def read(filename):
    """Reads records from csv file."""
    parsers = {
        "date": parse_date_string,
        "opened_unix": lambda s: datetime.fromtimestamp(int(s)) if s else None,
        "solved_unix": lambda s: datetime.fromtimestamp(int(s)) if s else None,
        "cheated": lambda s: s == "true",
        "solve_time_secs": lambda s: int(s) if s else None,
    }
    I = lambda x: x

    def parse(r):
        return {k: parsers.get(k, I)(v) for k, v in r.items()}

    try:
        with open(filename) as f:
            reader = csv.DictReader(f)
            return [parse(r) for r in reader]
    except FileNotFoundError as e:
        print(e)
        return []


def missing_days(data, dates):
    have_solve_data = {d["date"] for d in data if d["solve_time_secs"]}
    return [d for d in dates if d not in have_solve_data]


def prep_for_writing(data):
    """Counterpart of read, formats data for writing, and preps for merging"""
    formatters = {
        "date": format_date,
        "opened_unix": lambda dt: int(dt.timestamp()) if dt else "",
        "solved_unix": lambda dt: int(dt.timestamp()) if dt else "",
        "cheated": lambda b: str(b).lower(),
        # 'solve_time_secs': str
    }
    I = lambda x: x

    def fmt(r):
        return {k: formatters.get(k, I)(v) for k, v in r.items()}

    formatted = [fmt(r) for r in data]

    return {r["date"]: r for r in formatted}


def merge(r1, r2):
    """Merges two sets of records and returns them sorted by date."""
    merged = r1 | r2
    return [v for (k, v) in sorted(merged.items(), key=lambda kv: kv[0])]


def store(filename, data, stats):
    old = prep_for_writing(data)

    records = {}
    for pi in stats:
        date_str = pi["print_date"]
        record = {
            "date": date_str,
            "puzzle_id": pi["puzzle_id"],
            "weekday": parse_date_string(date_str).strftime("%a"),
        }
        solved = pi["calcs"].get("solved", False)
        if solved:
            cheated = any(c in pi["firsts"] for c in ["checked", "revealed"])
            record.update(
                {
                    "solve_time_secs": pi["calcs"]["secondsSpentSolving"],
                    "opened_unix": pi["firsts"]["opened"],
                    "solved_unix": pi["firsts"]["solved"],
                    "cheated": str(cheated).lower(),
                }
            )
        else:
            record.update(
                {
                    "cheated": "false",
                }
            )
        records[date_str] = record

    merged = merge(old, records)

    # Write data in the format @kesyog uses.
    h = "date,puzzle_id,weekday,solve_time_secs,opened_unix,solved_unix,cheated"
    fieldnames = h.split(",")
    with open(filename, "w") as f:
        w = csv.DictWriter(f, fieldnames)
        w.writeheader()
        w.writerows(merged)
