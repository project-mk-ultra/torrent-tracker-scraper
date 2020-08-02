import pytest

from torrent_tracker_scraper import scraper


@pytest.fixture
def good_infohashes():
    return [
        "88334ec1d90afe94a22c6de5756268599f5f8ea2",
        "5b6a484a018beed4d01f2f57e6d029a4190a9d04",
    ]


@pytest.fixture
def mixed_infohashes():
    return [
        "88334ec1d90afe94a22c",
        "6de5756268599f5f8ea2",
        "5b6a484a018beed",
        "4d01f2f57e6d029a4190a9d04",
        "88334ec1d90afe94a22c6de5756268599f5f8ea2",
        "5b6a484a018beed4d01f2f57e6d029a4190a9d04",
    ]


def test_parse_none_infohashes():
    _scraper = scraper.Scraper()
    assert _scraper.parse_infohashes() == []


def test_parse_empty_infohashes():
    _scraper = scraper.Scraper(infohashes=[])
    assert _scraper.parse_infohashes() == []


def test_single_infohash_parsing(good_infohashes):
    _scraper = scraper.Scraper(infohashes=good_infohashes[0])
    assert _scraper.parse_infohashes() == [good_infohashes[0]]


def test_multiple_infohashes_parsing(good_infohashes):
    _scraper = scraper.Scraper(infohashes=good_infohashes)
    assert _scraper.parse_infohashes() == good_infohashes


def test_string_type_infohashes_parsing(good_infohashes):
    _scraper = scraper.Scraper(
        infohashes="88334ec1d90afe94a22c6de5756268599f5f8ea2,5b6a484a018beed4d01f2f57e6d029a4190a9d04"
    )
    assert _scraper.parse_infohashes() == good_infohashes


def test_string_type_infohashes_parsing_with_multiple_commas(good_infohashes):
    _scraper = scraper.Scraper(
        infohashes="88334ec1d90afe94a22c6de5756268599f5f8ea2,5b6a484a018beed4d01f2f57e6d029a4190a9d04, , ,"
    )
    assert _scraper.parse_infohashes() == good_infohashes


def test_bad_infohash_parsing(mixed_infohashes):
    _scraper = scraper.Scraper(infohashes=["88334ec1d90afe94a22c6de575626"])
    assert _scraper.parse_infohashes() == []
    _scraper = scraper.Scraper(infohashes=mixed_infohashes)
    assert _scraper.parse_infohashes() == [
        "88334ec1d90afe94a22c6de5756268599f5f8ea2",
        "5b6a484a018beed4d01f2f57e6d029a4190a9d04",
    ]


def test_get_trackers():
    _scraper = scraper.Scraper()
    assert type(_scraper.get_trackers()) == list
