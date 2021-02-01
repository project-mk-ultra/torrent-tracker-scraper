from socket import socket

import pytest, os
from torrent_tracker_scraper import scraper
from torrent_tracker_scraper.scraper import Connection

# TODO: Improve tests: fixtures, mocks


@pytest.fixture
def scraper_basic():
    """
    Returns scraper instance initialized with trackers and infohashes.
    """
    scraper_ = scraper.Scraper(
        trackers=["udp://bt2.archive.org:6969"],
        infohashes=["73C36F980F5B1A40348678036575CCC1E0BB0E4E"],
    )
    scraper_.connection = Connection("bt2.archive.org", 6969, 10)

    # Use together
    scraper_.connect_response = b"\x00\x00\x00\x00\x00\x008@P\x87\xe0m\x108\xf6r"
    scraper_.transaction_id = 14400  # fixed in return value of socket.recv
    scraper_.connection_id = (
        5802853403918399090  #  fixed in return value of socket.recv
    )

    return scraper_


@pytest.fixture
def mock_response():
    return [
        {
            "tracker": "udp//:bt2.archive.org:6969",
            "results": [
                {
                    "infohash": "73C36F980F5B1A40348678036575CCC1E0BB0E4E",
                    "seeders": 0,
                    "completed": 0,
                    "leechers": 0,
                }
            ],
        }
    ]


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


def test_get_good_infohashes():
    scraper_ = scraper.Scraper()
    assert scraper_.get_good_infohashes() == []


def test_get_good_infohashes_empty_list():
    scraper_ = scraper.Scraper(infohashes=[])
    assert scraper_.get_good_infohashes() == []


def test_get_good_infohashes_single_infohash(good_infohashes):
    scraper_ = scraper.Scraper(infohashes=good_infohashes[0])
    assert scraper_.get_good_infohashes() == [good_infohashes[0]]


def test_get_good_infohashes_with_multiple_infohashes(good_infohashes):
    scraper_ = scraper.Scraper(infohashes=good_infohashes)
    assert scraper_.get_good_infohashes() == good_infohashes


def test_get_good_infohashes_string_type_infohashes(good_infohashes):
    scraper_ = scraper.Scraper(
        infohashes="88334ec1d90afe94a22c6de5756268599f5f8ea2,5b6a484a018beed4d01f2f57e6d029a4190a9d04"
    )
    assert scraper_.get_good_infohashes() == good_infohashes


def test_get_good_infohashes_string_type_with_multiple_commas(good_infohashes):
    scraper_ = scraper.Scraper(
        infohashes="88334ec1d90afe94a22c6de5756268599f5f8ea2,5b6a484a018beed4d01f2f57e6d029a4190a9d04, , ,"
    )
    assert scraper_.get_good_infohashes() == good_infohashes


def test_get_good_infohashes_bad_infohash(mixed_infohashes):
    scraper_ = scraper.Scraper(infohashes=["88334ec1d90afe94a22c6de575626"])
    assert scraper_.get_good_infohashes() == []
    scraper_ = scraper.Scraper(infohashes=mixed_infohashes)
    assert scraper_.get_good_infohashes() == [
        "88334ec1d90afe94a22c6de5756268599f5f8ea2",
        "5b6a484a018beed4d01f2f57e6d029a4190a9d04",
    ]


def test_get_trackers_return_type(scraper_basic):
    assert type(scraper_basic.get_trackers()) == list


def test_connect_request_success(monkeypatch, scraper_basic):
    recv = lambda s, f: scraper_basic.connect_response
    monkeypatch.setattr(socket, "recv", recv)
    response_transaction_id, connection_id, _ = scraper_basic._connect_request(
        scraper_basic.transaction_id
    )

    assert (response_transaction_id, connection_id) == (
        scraper_basic.transaction_id,
        scraper_basic.connection_id,
    )


def test_connect_request_failure(monkeypatch, scraper_basic):
    recv = lambda s, f: b"\x00\x00\x00\x00"
    monkeypatch.setattr(socket, "recv", recv)
    transaction_id, _, error = scraper_basic._connect_request(123)

    assert transaction_id == 0
    assert error is not None
