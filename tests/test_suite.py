# tests/test_suite.py
import unittest

from tests.scraper_test import ScrapeTest


def test_suite():
    suite = unittest.TestSuite()

    suite.addTests([ScrapeTest])
