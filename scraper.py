import collections
import threading
import time


class Scraper:
    def __init__(self, session, threads=10, qps=5):
        self.session = session
        self.semaphore = threading.Semaphore(threads)
        self.qps = qps
        self.timestamps = collections.deque(maxlen=self.qps)

    def wait_for_rate_limit(self):
        while True:
            now = time.monotonic()
            while self.timestamps and self.timestamps[0] <= now - 1:
                self.timestamps.popleft()

            if len(self.timestamps) < self.qps:
                break
            time.sleep(0.05)

    def get(self, url):
        with self.semaphore:
            self.wait_for_rate_limit()

            response = self.session.get(url)

            self.timestamps.append(time.monotonic())
            return response.json()
