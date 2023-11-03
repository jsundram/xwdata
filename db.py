import os

from statsfile import StatsFile
from datadir import DataDir


class Data:
    FULL_STATS = "full_stats"
    PUZZLE = "puzzle"
    STATS = "stats"

    def stat_kinds():
        return [Data.STATS, Data.FULL_STATS]


class Puzzle:
    DAILY = "daily"
    MINI = "mini"

    def types():
        return [Puzzle.MINI, Puzzle.DAILY]


class DB:
    def __init__(self, directory, puzzle_types, stat_kinds, puzzles, uid):
        """Args:
        directory: to read/write from/to; created if it doesn't exist.
        begin: datetime at which to begin (don't read data before this date)
        puzzle_types: list with one or both of ['mini', 'daily']
        stat_kinds: list with one or both of ['stats', 'full_stats']
        puzzles: bool telling whether we want to get the puzzles
        uid: user_id for stats
        """
        os.makedirs(directory, exist_ok=True)
        self.dir = directory

        constructors = {
            Data.FULL_STATS: lambda r: DataDir(r, Data.STATS),
            Data.PUZZLE: lambda r: DataDir(r, Data.PUZZLE),
            Data.STATS: StatsFile,
        }
        root = {
            Data.FULL_STATS: os.path.join(uid, Data.FULL_STATS),
            Data.PUZZLE: Data.PUZZLE + "s",
            Data.STATS: os.path.join(uid, Data.STATS),
        }
        ending = {Data.STATS: ".csv"}

        dbs = {}
        kinds = stat_kinds + [Data.PUZZLE] if puzzles else stat_kinds
        for k in kinds:
            dbs[k] = {}
            new = constructors[k]
            for p in puzzle_types:
                path = os.path.join(directory, root[k], p) + ending.get(k, "")
                dbs[k][p] = new(path)
        self.dbs = dbs

    def read(self, begin):
        for kind in self.dbs:
            for ptype in self.dbs[kind]:
                self.dbs[kind][ptype].read(begin)

    def missing_days(self, dates, data_kind, puzzle_type):
        return self.dbs[data_kind][puzzle_type].missing_days(dates)

    def store(self, data, kind_or_kinds, puzzle_type):
        match kind_or_kinds:
            case str():
                if kind_or_kinds != Data.PUZZLE:
                    raise TypeError("Unsupported type")
                self.dbs[kind_or_kinds][puzzle_type].write(data)
            case list():
                for stat in kind_or_kinds:
                    self.dbs[stat][puzzle_type].write(data)
            case _:
                raise TypeError("Unsupported type")
