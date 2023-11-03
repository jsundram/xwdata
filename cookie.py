#!/usr/bin/env python3

import json
import sys

"""
Cookie Utils
TODO:
* add a login method to try to use username/password to create cookie.json
"""


def read_auth_cookie(filename):
    cookies = {}
    # There's a lot of stuff that we don't need to auth.
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pairs = line.split("; ")
            for p in pairs:
                k, v = p.split("=", maxsplit=1)
                cookies[k] = v

    print("Read cookies:\n")
    print(json.dumps(cookies, indent=4))
    cred = "NYT-S"
    if cred not in cookies:
        raise AttributeError("Missing %s cookie" % cred)

    return {cred: cookies[cred]}


def save_cookie(cookie, filename):
    with open(filename, "w") as f:
        json.dump(cookie, f, indent=4)

    print("\nSaved %s to %s." % (list(cookie.keys())[0], filename))


def main(filename):
    """Need to get an NYT Login Cookie (NYT-S), easiest way is in Chrome:
    1. Open Developer Tools | Network
    2. Press the Fetch/XHR button.
    3. Load https://www.nytimes.com/crosswords
    4. Click on v2, or any of the .json files in the "Name" column
    5. Click on the Headers section
    6. Scroll down until you see "Cookie:"
    7. Triple click the gobbledygook to select it all, and copy it (Ctrl-C)
    8. Paste it in a file called cookie.txt

    Then you can run this program, and your cookie.txt will be
    transformed into a file called cookie.json, which has your NYT-S
    cookie (but has ignored all the other ones).
    """
    cookie = read_auth_cookie(filename)
    save_cookie(cookie, filename.replace(".txt", ".json"))


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Usage: `python3 cookie.py filename.txt`")
    else:
        main(filename)
