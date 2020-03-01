import os

import pytest

from torrent_tracker_scraper.scraper import Scraper


def lines_to_list(path):
    f = open(path, 'r')
    content = f.readlines()
    content = map(lambda line: line.replace('\n', ''), content)
    return list(content)


@pytest.fixture
def good_infohashes():
    good_infohashes_path = os.path.join(
        os.path.dirname(__file__), 'good_infohashes.txt')
    good_infohashes = lines_to_list(good_infohashes_path)
    return good_infohashes


@pytest.fixture
def bad_infohashes():
    bad_infohashes_path = os.path.join(
        os.path.dirname(__file__), 'bad_infohashes.txt')
    bad_infohashes = lines_to_list(bad_infohashes_path)
    return bad_infohashes


def test_scrape_with_good_infohash(good_infohashes):
    _scraper = Scraper("tracker.coppersuffer.tk", 6969, json=True, timeout=15)
    results = _scraper.scrape(good_infohashes[0])
    assert len(results.get('results')) == 1


def test_scrape_with_good_infohashes(good_infohashes):
    _scraper = Scraper("tracker.coppersuffer.tk", 6969, json=True, timeout=15)
    results = _scraper.scrape(good_infohashes)
    assert len(results.get('results')) == 2


def test_scrape_with_bad_infohashes(bad_infohashes):
    _scraper = Scraper("tracker.coppersuffer.tk", 6969, json=True, timeout=15)
    results = _scraper.scrape(bad_infohashes)
    assert results.get('results')[1].get('error') is not None
