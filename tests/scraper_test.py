# tests/scrape_test.py
import unittest

import scraper


class ScrapeTest(unittest.TestCase):

    def test_scraper(self):
        f = open('../good_infohashes.txt', 'rb')

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
        f = open('../bad_infohashes.txt', 'rb')

        content = f.readlines()

        for infohash in content:
            infohash = infohash.decode('utf-8')
            infohash = infohash.strip()
            error = scraper.scrape(infohash,
                                   "tracker.coppersurfer.tk",
                                   6969)
            self.assertEqual(error, "Invalid infohash {0}".format(infohash))

        f.close()
