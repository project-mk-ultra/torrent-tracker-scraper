# tests/scrape_test.py
import os
import unittest

from scraper import Scraper

GOOD_INFOHASHES_PATH = os.path.join(os.path.dirname(__file__), 'good_infohashes.txt')
BAD_INFOHASHES_PATH = os.path.join(os.path.dirname(__file__), 'bad_infohashes.txt')


class ScrapeTest(unittest.TestCase):

    def test_scraper_with_single_infohash(self):
        f = open(GOOD_INFOHASHES_PATH, 'rb')

        content = f.readlines()

        for infohash in content:
            infohash = infohash.decode('utf-8')
            infohash = infohash.strip()
            _scraper = Scraper("tracker.coppersuffer.tk", 6969, json=True)
            results = _scraper.scrape(infohash)
            self.assertEqual(results.get('results')[0].get('infohash'), infohash)

        f.close()

    def test_scraper_with_single_bad_infohash(self):
        f = open(BAD_INFOHASHES_PATH, 'rb')

        content = f.readlines()

        for infohash in content:
            infohash = infohash.decode('utf-8')
            infohash = infohash.strip()
            _scraper = Scraper("tracker.coppersuffer.tk", 6969, json=True)
            results = _scraper.scrape(infohash)
            self.assertEqual(results, "Invalid infohash {0}, skipping".format(infohash))

        f.close()

    def test_bad_tracker(self):
        f = open(GOOD_INFOHASHES_PATH, 'rb')

        content = f.readlines()

        for infohash in content:
            infohash = infohash.decode('utf-8')
            infohash = infohash.strip()
            _scraper = Scraper("invalidhostname.tk", 6969, json=True)
            error = _scraper.scrape(infohash)
            breakpoint()
            self.assertEqual(tuple, type(error))

        f.close()
