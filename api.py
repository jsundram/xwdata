import json
import requests
import yaml
from tqdm import tqdm

from utils import format_date, chunk_dates


def get_session(cookie_file):
    with open(cookie_file) as f:
        cookie = json.load(f)

    session = requests.Session()
    for k, v in cookie.items():
        session.cookies.set(k, v)
    return session


def get_config(config_file):
    with open(config_file) as f:
        return yaml.safe_load(f)


def get_user_id(session, config):
    r = session.post(config["url"], json=config["query"], headers=config["headers"])
    try:
        # TODO: check r.status_code?
        result = r.json()
        return result["data"]["user"]["userInfo"]["regiId"]
    except Exception as e:
        print(e)
        # continue the long tradition of hard-coding the developer's own id...
        return "61484727"


class Api:
    def __init__(self, config_file, cookie_file):
        config = get_config(config_file)
        self.session = get_session(cookie_file)

        self.user_id = get_user_id(self.session, config["user"])
        config["info"]["url"] = config["info"]["url"].format(userId=self.user_id)
        self.config = config

    @property
    def threads(self):
        return self.config["general"]["threads"]

    @property
    def qps(self):
        return self.config["general"]["qps"]

    def get_puzzle_url(self, date, puzzle_type):
        config = self.config["puzzle"]
        args = {"type": puzzle_type, "date-str": format_date(date)}
        return config["url"].format(**args)

    def get_stats_url(self, puzzle_info):
        """puzzle_info is an object returned from get_puzzle_info
        Importantly, it needs to have a property puzzle_id
        """
        return self.config["stats"]["url"].format(**puzzle_info)

    def get_puzzle_info(self, dates, puzzle_type):
        """Hits the API to find puzzle ids for all the dates given.
        returns a list of puzzle ids along with their publish date:
            [{'date': datetime, 'puzzle_id': str}, ...]
        puzzle_type is one of {'daily', 'mini'}
        """
        config = self.config["info"]

        def get_args(chunk):
            d1, d2 = chunk
            return {
                "publish_type": puzzle_type,
                "sort_order": "asc",
                "sort_by": "print_date",
                "date_start": format_date(d1),
                "date_end": format_date(d2),
            }

        results = []
        chunks = chunk_dates(dates, size=config["max-chunk-size"])
        no_progress = len(chunks) == 0
        progress_bar = tqdm(chunks, disable=no_progress, desc="getting info")
        for chunk in progress_bar:
            args = get_args(chunk)
            status = "%s - %s" % (args["date_start"], args["date_end"])
            progress_bar.set_postfix_str(status)
            r = self.session.get(config["url"], params=args, headers=config["headers"])
            j = r.json()
            if j.get("status") == "OK":
                results.extend(j.get("results", []))
        return results
