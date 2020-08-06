# !/usr/bin/env python
# scrape.py
import binascii
import io
import logging
import random
import socket
import struct
import time
from multiprocessing import Pool
from urllib.parse import urlparse

import requests

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Protocol says to keep it that way (https://www.bittorrent.org/beps/bep_0015.html)
PROTOCOL_ID = 0x41727101980


class TRACKER_ACTION:
    CONNECT = 0
    SCRAPE = 2


def is_infohash_valid(infohash: str) -> bool:
    """
    Checks if the infohash is 20 bytes long, confirming its truly of SHA-1 nature
    :param infohash:
    :return: True if infohash is valid, False otherwise
    """
    if not isinstance(infohash, str):
        return False

    if len(infohash) == 40:
        return True
    return False


def filter_valid_infohashes(infohashes: list) -> list:
    """Returns a list with only valid infohashes"""
    return list(filter(lambda i: is_infohash_valid(i), infohashes))


def is_not_blank(s: str) -> bool:
    return bool(s and s.strip())


class Connection:
    def __init__(self, hostname, port, timeout):
        self.hostname = hostname
        self.port = port
        self.sock = self.connect(timeout)

    def connect(self, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        try:
            sock.connect((self.hostname, self.port))
        except socket.error as e:
            sock.close()
            logger.warning(
                "Could not connect to %s:%s: %s", self.hostname, self.port, e
            )
            return None
        return sock

    def close(self):
        """Closes a socket connection gracefully"""
        if self.sock:
            self.sock.close()


class Scraper:
    def __init__(self, trackers=[], infohashes=[], timeout=10):
        """
        Launches a scraper bound to a particular tracker
        :Keyword Arguments:
            :param trackers (list): An array of trackers in the url format e.g udp://tracker.coppersurfer.tk:6969/announce
            :param infohashes (list): List of infohashes SHA-1 representation of the ```info``` key in the torrent file that should be parsed e.g. 95105D919C10E64AE4FA31067A8D37CCD33FE92D
            :param timeout (int): Timeout value in seconds, program exits if no response received within this period
        """
        self.trackers = trackers
        self.infohashes = infohashes
        self.timeout = timeout

    def parse_infohashes(self) -> list:
        infohashes = self.infohashes
        if isinstance(infohashes, str):
            _infohashes = infohashes.split(",")
            infohashes = filter_valid_infohashes(_infohashes)
        elif isinstance(infohashes, list):
            infohashes = filter_valid_infohashes(infohashes)
        return infohashes

    def get_trackers(self) -> list:
        if not self.trackers:
            trackers = list()
            response = requests.get("https://newtrackon.com/api/stable")
            response = io.StringIO(response.text)
            for line in response.readlines():
                if is_not_blank(line):
                    line = line.rstrip()
                    trackers.append(line)
        else:
            trackers = self.trackers
        trackers = list(map(lambda tracker: urlparse(tracker), trackers))
        trackers = list(filter(lambda tracker: tracker.scheme == "udp", trackers))
        logger.debug("Got trackers: %s", trackers)
        return trackers

    def get_transaction_id(self):
        return random.randrange(1, 65535)

    def _connect_request(self, transaction_id):
        # Send a Connect Request
        packet = struct.pack(
            ">QLL", PROTOCOL_ID, TRACKER_ACTION.CONNECT, transaction_id
        )
        self.connection.sock.send(packet)

        # Receive a Connect Request response
        res = self.connection.sock.recv(16)
        logger.info("### res connect: %s", res)
        try:
            _, response_transaction_id, connection_id = struct.unpack(">LLQ", res)
        except struct.error as e:
            logger.error("Unpacking connect request response failed: %s", e)
            raise Exception("Unpacking connect request response failed: %s" % e)

        return response_transaction_id, connection_id

    def scrape_tracker(self, tracker):
        """
        To understand how data is retrieved visit: https://www.bittorrent.org/beps/bep_0015.html
        """

        self.connection = Connection(tracker.hostname, tracker.port, self.timeout)

        # Quit scraping if there is no connection
        if self.connection.sock is None:
            return []

        # We should get the same value in a response
        transaction_id = self.get_transaction_id()

        response_transaction_id, connection_id = self._connect_request(transaction_id)
        logger.info("### connection : %s", connection_id)
        if transaction_id != response_transaction_id:
            logger.error(
                "Transactions IDs do not match. Connect request: %d Connect response: %d",
                transaction_id,
                response_transaction_id,
            )
            raise Exception(
                f"Transactions IDs do not match. Connect request: {transaction_id} Connect response: {response_transaction_id}"
            )

        results = list()

        logger.debug("Parsing list of infohashes [%s]", tracker.netloc)
        # holds good infohashes for unpacking, used to weed out bad infohashes
        _good_infohashes = list()
        # holds bad error messages
        _bad_infohashes = list()
        packet_hashes = bytearray(str(), "utf-8")
        for infohash in self.infohashes:
            if not is_infohash_valid(infohash):
                _bad_infohashes.append({"infohash": infohash, "error": "Bad infohash"})
                continue
            try:
                packet_hashes += binascii.unhexlify(infohash)
                _good_infohashes.append(infohash)
            except TypeError as e:
                _bad_infohashes.append({"infohash": infohash, "error": e})
                continue
        packet = (
            struct.pack(">QLL", connection_id, TRACKER_ACTION.SCRAPE, transaction_id)
            + packet_hashes
        )
        self.connection.sock.send(packet)

        # Scrape response
        try:
            res = self.connection.sock.recv(8 + (12 * len(self.infohashes)))
        except socket.timeout as e:
            logger.error("socket.timeout: %s", e)
            return ["socket.timeout error"]

        index = 8
        # TODO: Current implementation don't show correct results.
        # We iterate through valid infohashes
        # and when merging received data with infohash we assume that
        # currect infohash is at the same index in self.infohashes

        # It happens when lenght self.infohashes != good_infohashes (because of filtering L180)
        for i in range(1, len(_good_infohashes) + 1):
            logger.debug("response: %s", res)
            logger.debug(
                "Offset: {} {}".format(index + (i * 12) - 12, index + (i * 12))
            )
            seeders, completed, leechers = struct.unpack(
                ">LLL", res[index + (i * 12) - 12 : index + (i * 12)]
            )
            results.append(
                {
                    "infohash": self.infohashes[i - 1],
                    "seeders": seeders,
                    "completed": completed,
                    "leechers": leechers,
                }
            )
        results += _bad_infohashes
        tracker = f"{tracker.scheme}//:{tracker.netloc}"
        return {"tracker": tracker, "results": results}

    def scrape(self):
        """
        Takes in an infohash or infohashes. Returns seeders, leechers and completed
        information
        :param infohashes: SHA-1 representation of the ```info``` key in the torrent file
        :return: [(infohash, seeders, leechers, completed),...]
        """

        self.trackers = self.get_trackers()

        infohashes = self.parse_infohashes()
        if not infohashes:
            logger.info("Nothing to do. No infohashes passed the checks")
            return []

        logger.info(f"Scraping infohashes: {infohashes}")

        p = Pool()
        results = p.map_async(self.scrape_tracker, self.trackers)
        p.close()
        while True:
            if results.ready():
                break
            time.sleep(0.3)
        results = list(filter(lambda result: result != [], results.get()))

        return results
