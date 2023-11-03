# XWData (Crossword Data) README
## Intro
This is my New York Times Crossword data scraper. There are many like it, but this one is mine. In particular, this code can pull stats for the mini as well as the daily puzzle, and can pull the puzzle data (clues, layout) as well.  This one was heavily influenced by [@keysog](https://github.com/kesyog/crossword/)'s implementation in Rust and a desire to extend it as well as separate the visualization code from the data retrieval code.

## Cookie
In order to use this, you need to get an NYT Login Cookie (NYT-S); the easiest way is as follows: 
1. In Chrome, Open Developer Tools | Network
2. Press the Fetch/XHR button.
3. Load https://www.nytimes.com/crosswords
4. Click on v2, or any of the .json files in the "Name" column
5. Click on the Headers section
6. Scroll down until you see "Cookie:"
7. Triple click the gobbledygook to select it all, and copy it (Ctrl-C)
8. Paste it in a file called cookie.txt
9. run `python3 cookie.py cookie.txt`. This will create a file called cookie.json, which has the value of your NYT-S saved (other values are ignored). 
10. You can now delete cookie.txt if you wish

## Usage:

Once you have created the cookie.json file (See *Cookie* above), you are ready to get your data.

### Sample Usage

`python3 main.py DATA_DIR -b 2023-11-1 -n my_cookie.json`

Full usage details (via `python3 main.py -h`)

```
usage: main.py [-h] [-c CONFIG] [-n NYTS_COOKIE] [-b BEGIN] [-d | --daily | --no-daily] [-m | --mini | --no-mini] [-p | --puzzle | --no-puzzle] [-s | --stats | --no-stats] [-f | --full-stats | --no-full-stats]
               data_dir

Retrieves NYT crossword data.

positional arguments:
  data_dir
      The path where data will be read from & stored

options:
  -h, --help            
      Show this help message and exit
  -c CONFIG, --config CONFIG
      The path to the nytimes api config file (default: api-config.yaml)
  -n NYTS_COOKIE, --nyts-cookie NYTS_COOKIE
      The path to a cookie.json file containing the NYT-S token (default: cookie.json)
  -b BEGIN, --begin BEGIN
      start date (default 2020-1-1). Discards all data before this date. (default: 2020-01-01)
  -d, --daily, --no-daily
      Retrieve Daily (puzzle | stats | full_stats) (default: True)
  -m, --mini, --no-mini
      Retrieve Mini (puzzle | stats | full_stats) (default: True)
  -p, --puzzle, --no-puzzle
      Retrieve Puzzle (daily | mini) (default: True)
  -s, --stats, --no-stats
      Retrieve Summary Stats (daily | mini) (default: True)
  -f, --full-stats, --no-full-stats
      Retrieve Stats json (daily | mini) (default: True)
```



The program will create the directory you pass in  (DATA_DIR above) if it doesn't exist, and create the following folder structure, where `{userid}` indicates your NYT userid (so if you are running this for multiple family members, you wont clobber/overwrite data).

```
/DATA_DIR/
    puzzles/
        mini/
            2023/11/puzzle-01.json
            2023/11/puzzle-02.json            
        daily/
            2023/11/puzzle-02.json
            2023/11/puzzle-02.json
    {userid}/
        stats/
            daily.csv
            mini.csv
				full_stats/            
            mini/
                2020/09/30/stats.json
            daily/
                2020/09/30/stats.json
```

