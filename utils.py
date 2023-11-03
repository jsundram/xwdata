from datetime import datetime, timedelta
from itertools import islice


def parse_date_string(s):
    return datetime.strptime(s, "%Y-%m-%d")


def format_date(dt):
    # if isinstance(dt, str): return dt
    return dt.strftime("%Y-%m-%d")


def date_range(start, end):
    """returns a list of datetimes | start <= dt <= end"""
    return [start + timedelta(i) for i in range((end - start).days + 1)]


def chunker(it, size):
    """via https://stackoverflow.com/a/61435714/2683"""
    iterator = iter(it)
    while chunk := list(islice(iterator, size)):
        yield chunk


def split_into_continuous_chunks(dates):
    chunks = []
    if dates:
        start, end = dates[0], None
        for d1, d2 in zip(dates, dates[1:]):
            continuous = (d2 - d1).days == 1
            if continuous:
                end = d2
            else:  # discontinuity; make new chunk
                if not end:
                    end = d1
                chunks.append((start, end))
                start, end = d2, None

        if not end:
            end = start
        chunks.append((start, end))
    return chunks


def chunk_dates(dates, size):
    """Breaks a list of potentially non-continuous dates into sub-ranges of
    `size` no bigger than size.
    """
    ccs = split_into_continuous_chunks(dates)
    chunks = []
    for start, end in ccs:
        dr = date_range(start, end)
        if len(dr) <= size:
            chunks.append((start, end))
        else:  # need to split
            for chunk in chunker(dr, size):
                chunks.append((chunk[0], chunk[-1]))
    return chunks
