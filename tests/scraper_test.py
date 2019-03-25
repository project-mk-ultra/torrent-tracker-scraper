# tests/scrape_test.py
import os
import unittest

from torrent_tracker_scraper import scraper

GOOD_INFOHASHES_PATH = os.path.join(os.path.dirname(__file__), 'good_infohashes.txt')
BAD_INFOHASHES_PATH = os.path.join(os.path.dirname(__file__), 'bad_infohashes.txt')


class ScrapeTest(unittest.TestCase):

    def test_scraper(self):
        f = open(GOOD_INFOHASHES_PATH, 'rb')

        content = f.readlines()

        for infohash in content:
            infohash = infohash.decode('utf-8')
            infohash = infohash.strip()
            torrent_infohash, seeders, leechers, complete = scraper.scrape(
                infohash,
                "tracker.coppersurfer.tk",
                6969
            )
            self.assertEqual(torrent_infohash, infohash)

        f.close()

    def test_scraper_infohash_error(self):
        f = open(BAD_INFOHASHES_PATH, 'rb')

        content = f.readlines()

        for infohash in content:
            infohash = infohash.decode('utf-8')
            infohash = infohash.strip()
            error = scraper.scrape(infohash,
                                   "tracker.coppersurfer.tk",
                                   6969)
            self.assertEqual(error, "Invalid infohash {0}".format(infohash))

        f.close()

    def test_bad_tracker(self):
        f = open(GOOD_INFOHASHES_PATH, 'rb')

        content = f.readlines()

        for infohash in content:
            infohash = infohash.decode('utf-8')
            infohash = infohash.strip()
            error = scraper.scrape(
                infohash,
                "invalidhostname.tk",
                6969
            )
            self.assertEqual(tuple, type(error))

        f.close()
