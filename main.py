#!/usr/bin/env python3
from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
    BooleanOptionalAction as boolopt,
)
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from tqdm import tqdm

import pathlib
import os

import api
from db import DB, Data, Puzzle
from scraper import Scraper
from utils import parse_date_string, date_range


A = ArgumentParser(
    description="Retrieves NYT crossword data.",
    formatter_class=ArgumentDefaultsHelpFormatter,
)

A.add_argument(
    "data_dir",
    action="store",
    type=str,
    help="The path where data will be read from & stored",
)
A.add_argument(
    "-c",
    "--config",
    action="store",
    type=str,
    default="api-config.yaml",
    help="The path to the nytimes api config file",
)
A.add_argument(
    "-n",
    "--nyts-cookie",
    action="store",
    type=str,
    default="cookie.json",
    help="The path to a cookie.json file containing the NYT-S token",
)
A.add_argument(
    "-b",
    "--begin",
    action="store",
    type=parse_date_string,
    default=datetime(2020, 1, 1),
    help="start date (default 2020-1-1). Discards all data before this date.",
)
A.add_argument(
    "-d",
    "--daily",  # --no-daily
    action=boolopt,
    default=True,
    type=bool,
    help="Retrieve Daily (puzzle | stats | full_stats)",
)
A.add_argument(
    "-m",
    "--mini",  # --no-mini
    action=boolopt,
    default=True,
    type=bool,
    help="Retrieve Mini (puzzle | stats | full_stats)",
)
A.add_argument(
    "-p",
    "--puzzle",  # --no-puzzle
    action=boolopt,
    default=True,
    type=bool,
    help="Retrieve Puzzle (daily | mini)",
)
A.add_argument(
    "-s",
    "--stats",  # --no-stats
    action=boolopt,
    default=True,
    type=bool,
    help="Retrieve Summary Stats (daily | mini)",
)
A.add_argument(
    "-f",
    "--full-stats",  # --no-full-stats
    action=boolopt,
    default=True,
    type=bool,
    help="Retrieve Stats json (daily | mini)",
)


def validate_args(parser):
    args = parser.parse_args()

    # Need one of mini or daily
    if not args.mini and not args.daily:
        parser.error("Need to specify at least one of daily | mini!")

    # Need to specify some data to download!
    if not args.full_stats and not args.puzzle and not args.stats:
        parser.error("Need to specify at least one of full_stats | puzzle | stats")

    if not os.path.exists(args.nyts_cookie):
        err = (
            "Can't find %s; Consult README.md and use cookie.py to make it"
            % args.nyts_cookie
        )
        parser.error(err)

    if not os.path.exists(args.config):
        parent = pathlib.Path(__file__).parent.resolve()
        default = os.path.join(parent, os.path.basename(args.config))
        if os.path.exists(default):
            args.config = default
        else:
            parser.error("Can't locate %s" % args.config)

    return args


def get(nyt, urls, desc=""):
    scraper = Scraper(nyt.session, threads=nyt.threads, qps=nyt.qps)
    with ThreadPoolExecutor(max_workers=nyt.threads) as e:
        return list(tqdm(e.map(scraper.get, urls), total=len(urls), desc=desc))


def main():
    args = validate_args(A)
    nyt = api.Api(args.config, args.nyts_cookie)

    has_arg = lambda k: args.__dict__.get(k, False)
    stat_kinds = [k for k in Data.stat_kinds() if has_arg(k)]
    puzzle_types = [k for k in Puzzle.types() if has_arg(k)]

    uid = nyt.user_id
    database = DB(args.data_dir, puzzle_types, stat_kinds, args.puzzle, uid)
    database.read(args.begin)

    drange = date_range(args.begin, datetime.today())
    if args.puzzle:
        for ptype in puzzle_types:
            missing = database.missing_days(drange, Data.PUZZLE, ptype)
            urls = [nyt.get_puzzle_url(dt, ptype) for dt in missing]
            puzzles = get(nyt, urls, "Getting %s puzzles" % (ptype))
            database.store(puzzles, Data.PUZZLE, ptype)

    for ptype in puzzle_types:
        missing = set()
        for stat in stat_kinds:
            missing.update(database.missing_days(drange, stat, ptype))
        dates = sorted(missing)

        # Get puzzle info for missing dates
        pinfo = nyt.get_puzzle_info(dates, ptype)
        urls = [nyt.get_stats_url(p) for p in pinfo if p["solved"]]

        # Get stats for new solved puzzles
        stats = get(nyt, urls, "Getting %s stats" % ptype)
        assert len(solved) == len(stats), "misaligned puzzle info and stats"
        data = [(stat | pi) for (stat, pi) in zip(stats, solved)]

        database.store(data, stat_kinds, ptype)


if __name__ == "__main__":
    main()
