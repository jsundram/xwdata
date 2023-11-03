import json
import os
import pathlib
from datetime import datetime

from utils import parse_date_string


class DataDir:
    # TODO: consider storing data in a dictionary {date: json}
    def __init__(self, directory, basename):
        os.makedirs(directory, exist_ok=True)
        self.directory = pathlib.Path(directory)
        self.basename = basename
        self.data = None

    def date_to_path(self, dt, ensure_exists=True):
        month, day = ("%02d" % s for s in [dt.month, dt.day])

        filename = self.basename + "-" + day + ".json"
        path = self.directory.joinpath(str(dt.year), month, filename)
        if ensure_exists:
            os.makedirs(path.parent, exist_ok=True)

        return path

    def path_to_date(self, s):
        p = pathlib.Path(s)
        path = p.relative_to(self.directory)
        year, month, filename = path.parts

        n = len(self.basename + "-")
        day = filename[n : n + 2]
        return datetime(int(year), int(month), int(day))

    def read(self, begin):
        data = []
        for path in sorted(pathlib.Path(self.directory).rglob("*.json")):
            date = self.path_to_date(path)
            if begin <= date:
                with open(path) as f:
                    data.append(json.load(f))
        self.data = data
        return data

    def _get_date(self, d):
        """Get a date from a dict representing either a puzzle or stats."""
        # stats has an attribute "print_date", puzzle has "publicationDate"
        date_str = d.get("print_date", d.get("publicationDate"))
        return parse_date_string(date_str)

    def missing_days(self, dates):
        have_dates = {self._get_date(d) for d in self.data}
        return [d for d in dates if d not in have_dates]

    def write(self, data):
        for d in data:
            date = self._get_date(d)
            path = self.date_to_path(date)
            with open(path, "w") as f:
                json.dump(d, f, indent=4)
