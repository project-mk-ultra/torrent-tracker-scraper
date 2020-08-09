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
from typing import List, Tuple
from urllib.parse import urlparse

import requests

# TODO: Improve logger format to include process id
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


def get_transaction_id():
    return random.randrange(1, 65535)


class Connection:
    def __init__(self, hostname, port, timeout):
        self.hostname = hostname
        self.port = port
        self.sock = self.connect(timeout)

    def __str__(self) -> str:
        return f"{self.hostname}:{self.port}"

    def connect(self, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        try:
            sock.connect((self.hostname, self.port))
        except socket.error as e:
            sock.close()
            logger.warning("Could not connect to %s: %s", self, e)
            return None
        return sock

    def close(self):
        """Closes a socket connection gracefully"""
        if self.sock:
            self.sock.close()


class Scraper:
    def __init__(
        self, trackers: List = [], infohashes: Tuple[List, str] = [], timeout: int = 10
    ):
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

        self.good_infohashes = self.parse_infohashes()

    def parse_infohashes(self) -> list:
        infohashes = self.infohashes
        if isinstance(infohashes, str):
            infohashes_list = infohashes.split(",")
            infohashes = filter_valid_infohashes(infohashes_list)
        elif isinstance(infohashes, list):
            infohashes = filter_valid_infohashes(infohashes)
        else:
            logger.error(
                "Infohashes are not supported in type: %s. Only list of strings or comma separated string.",
                type(self.infohashes),
            )
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
        return trackers

    def _connect_request(self, transaction_id):
        # Send a Connect Request
        packet = struct.pack(
            ">QLL", PROTOCOL_ID, TRACKER_ACTION.CONNECT, transaction_id
        )
        self.connection.sock.send(packet)
        # Receive a Connect Request response
        res = self.connection.sock.recv(16)
        try:
            _, response_transaction_id, connection_id = struct.unpack(">LLQ", res)
        except struct.error as e:
            logger.error("Unpacking connect request response failed: %s", e)
            raise Exception("Unpacking connect request response failed: %s" % e)

        return response_transaction_id, connection_id

    def _scrape_response(self, transaction_id, connection_id):
        packet_hashes = self.get_packet_hashes()
        packet = (
            struct.pack(">QLL", connection_id, TRACKER_ACTION.SCRAPE, transaction_id,)
            + packet_hashes
        )
        self.connection.sock.send(packet)

        # Scrape response
        try:
            res = self.connection.sock.recv(8 + (12 * len(self.good_infohashes)))
        except socket.timeout as e:
            logger.error("Socket timeout for %s: %s", self.connection, e)
            return ["Socket timeout for %s: %s" % (self.connection, e)]

        # TODO: rename, it's first 8 bytes (4 action, 4 connection_id)
        index = 8
        results = list()
        for i, infohash in enumerate(self.good_infohashes, start=1):
            result = {
                "infohash": infohash,
            }

            response = res[index + (i * 12) - 12 : index + (i * 12)]
            if len(response) != struct.calcsize(">LLL"):
                # TODO: Improve error messages
                result[
                    "error"
                ] = f"Could not get stats for infohash [{self.connection}]"
                results.append(result)
                logger.error("Result error: %s", result)
                continue
            seeders, completed, leechers = struct.unpack(">LLL", response)
            results.append(
                {
                    "infohash": infohash,
                    "seeders": seeders,
                    "completed": completed,
                    "leechers": leechers,
                }
            )

        return results

    def get_packet_hashes(self):
        packet_hashes = bytearray(str(), "utf-8")
        for infohash in self.good_infohashes:
            try:
                packet_hashes += binascii.unhexlify(infohash)
            except binascii.Error as e:
                logger.warning(
                    "Infohash %s is invalid. Error when preparing packet hashes: %s",
                    infohash,
                    e,
                )

        return packet_hashes

    def scrape_tracker(self, tracker):
        """
        To understand how data is retrieved visit: https://www.bittorrent.org/beps/bep_0015.html
        """

        # logger.debug("Parsing list of infohashes [%s]", tracker.netloc)
        self.connection = Connection(tracker.hostname, tracker.port, self.timeout)
        tracker_url = f"{tracker.scheme}//:{tracker.netloc}"
        # Quit scraping if there is no connection
        if self.connection.sock is None:
            # TODO: Return info which tracker failed
            return []

        # We should get the same value in a response
        transaction_id = get_transaction_id()
        try:
            response_transaction_id, connection_id = self._connect_request(
                transaction_id,
            )
        except socket.timeout as e:
            logger.error("Socket timeout for %s: %s", self.connection, e)
            return ["Socket timeout for %s: %s" % (self.connection, e)]
        if transaction_id != response_transaction_id:
            logger.error(
                "Transactions IDs do not match. Connect request: %d Connect response: %d",
                transaction_id,
                response_transaction_id,
            )
            raise Exception(
                f"Transactions IDs do not match. Connect request: {transaction_id} Connect response: {response_transaction_id}"
            )

        # holds bad error messages
        _bad_infohashes = list()
        for infohash in self.infohashes:
            if not is_infohash_valid(infohash):
                _bad_infohashes.append({"infohash": infohash, "error": "Bad infohash"})

        results = self._scrape_response(transaction_id, connection_id)
        results += _bad_infohashes
        return {"tracker": tracker_url, "results": results}

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
