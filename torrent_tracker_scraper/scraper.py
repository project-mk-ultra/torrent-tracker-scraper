# !/usr/bin/env python
# scrape.py
import binascii
import json
import logging
import os
import random
import struct
from threading import Timer
import logging
import socket
import argparse
import logging


logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, hostname, port, timeout):
        self.hostname = hostname
        self.port = port
        self.sock = self.connect(
            self.hostname, self.port, timeout)

    def connect(self, hostname, port, timeout):
        # create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        try:
            # connect socket
            sock.connect((self.hostname, self.port))
            logger.debug(
                f'Successfully connected to {self.hostname} {self.port}. Set timeout to {timeout} secs.')
        except Exception as e:
            # handle socket connection error
            logger.error(
                "Tracker udp://{0}:{1} down falling back to udp://tracker.coppersurfer.tk".format(
                    hostname, port))
            try:
                sock.connect(("tracker.coppersurfer.tk", 6969))
                return sock
            except Exception as e:
                sock.close()
                logger.error(e, logging.ERROR)
                logger.error(
                    " Tracker udp://{0}:{1} is also down, check your Internet".format("tracker.coppersurfer.tk",
                                                                                      6969))
                return None
        return sock

    def close(self):
        """
        Closes a socket connection gracefully
        :return: None
        """
        self.sock.close()


class Scraper:
    def __init__(self, hostname, port, json=False, **kwargs):
        """
        Launches a scraper bound to a particular tracker
        :param hostname: Tracker hostname e.g. coppersuffer.tk
        :param port: 6969, self-explanatory
        :param json: dictates if a json object should be returned as the output
        :param TODO: timeout: Timeout value in seconds, program exits if no response received within this period
        """
        self.json = json
        self.timeout = kwargs.get('timeout', 3)
        self.connection = Connection(hostname, port, timeout=self.timeout)

    def parse_infohashes(self, infohashes):
        if isinstance(infohashes, str):
            if "," not in infohashes:
                if self.is_40_char_long(infohashes):
                    return [infohashes]
            if "," in infohashes:
                infohashes = infohashes.split(',')
                return list(filter(lambda infohash: self.is_40_char_long(infohash) is True, infohashes))
        if isinstance(infohashes, list):
            return list(filter(lambda infohash: self.is_40_char_long(infohash) is True, infohashes))
        return None

    def scrape(self, infohashes):
        """
        Takes in an infohash or infohashes. Returns seeders, leechers and completed
        information
        :param infohashes: SHA-1 representation of the ```info``` key in the torrent file
        :return: [(infohash, seeders, leechers, completed),...]
        """

        infohashes = self.parse_infohashes(infohashes)

        if infohashes is None or len(infohashes) == 0:
            logger.info("Nothing to do. No infohashes passed the checks")
            return []

        logger.debug(f'Scraping infohashes: {infohashes}')

        tracker_url = f'udp://{self.connection.hostname}:{self.connection.port}'

        # Quit scraping if there is no connection
        if self.connection.sock is None:
            return "Tracker {0} is down".format(tracker_url)

        # Protocol says to keep it that way
        protocol_id = 0x41727101980

        # We should get the same in response
        transaction_id = random.randrange(1, 65535)

        # Send a Connect Request
        packet = struct.pack(">QLL", protocol_id, 0, transaction_id)
        self.connection.sock.send(packet)

        # Receive a Connect Request response
        res = self.connection.sock.recv(16)
        action, transaction_id, connection_id = struct.unpack(">LLQ", res)

        results = list()

        logger.debug("Parsing list of infohashes")
        # holds good infohashes for unpacking, used to weed out bad infohashes
        _good_infohashes = list()
        # holds bad error messages
        _bad_results = list()
        packet_hashes = bytearray(str(), 'utf-8')
        for infohash in infohashes:
            if not self.is_40_char_long(infohash):
                _bad_results.append(
                    {"infohash": infohash, "error": "Bad infohash"})
                continue
            try:
                packet_hashes += binascii.unhexlify(infohash)
                _good_infohashes.append(infohash)
            except Exception as e:
                _bad_results.append(
                    {"infohash": infohash, "error": f'Error: {e}'})
                continue
        packet = struct.pack(">QLL", connection_id, 2,
                             transaction_id) + packet_hashes
        self.connection.sock.send(packet)

        # Scrape response
        try:
            res = self.connection.sock.recv(8 + (12 * len(infohashes)))
        except socket.timeout as e:
            logger.debug(f'socket.timeout {e}')
            return ['socket.timeout error']

        index = 8
        for i in range(1, len(_good_infohashes) + 1):
            logger.debug("Offset: {} {}".format(
                index + (i * 12) - 12, index + (i * 12)))
            seeders, completed, leechers = struct.unpack(
                ">LLL", res[index + (i * 12) - 12: index + (i * 12)])
            results.append({"infohash": infohashes[i - 1],
                            "seeders": seeders,
                            "completed": completed,
                            "leechers": leechers})
        results += _bad_results
        return results

    def is_40_char_long(self, s: str):
        """
        Checks if the infohash is 20 bytes long, confirming its truly of SHA-1 nature
        :param s:
        :return: True if infohash is valid, False otherwise
        """
        if len(s) == 40:
            return True
        return False

    def __del__(self):
        """
        Close connection if the scraper object is being destroyed
        :return: None
        """
        if self.connection is not None:
            self.connection.close()

    def __repr__(self):
        return f'{self.connection.hostname}:{self.connection.port}'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument("-i",
                          "--infohash",
                          help="A torrents infohash or a file path consisting of infohashes",
                          required=True)
    optional.add_argument("-t",
                          "--tracker",
                          help="Entered in the format :tracker",
                          type=str,
                          default="tracker.leechers-paradise.org")
    optional.add_argument("-p",
                          "--port",
                          help="Entered in the format :port",
                          type=int,
                          default=6969)
    optional.add_argument("-j",
                          "--json",
                          help="Outputs in JSON format. If you are thinking of going this route, I would suggesting using the tool module option, but hey...who am I to tell you what to do",
                          dest='json',
                          action='store_true')
    optional.add_argument("-to",
                          "--timeout",
                          help="Enter the timeout in seconds",
                          type=int,
                          default=3)
    optional.add_argument("-v",
                          "--verbose",
                          help="Increase verbosity for debugging purposes",
                          action="store_true")
    parser.set_defaults(json=False)

    args, unknown = parser.parse_known_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='[%(levelname)s]: %(message)s')
    logger.debug("Logger initialised")

    scraper = Scraper(args.tracker, args.port, args.json, timeout=args.timeout)
    results = scraper.scrape(args.infohash)
    if args.json:
        print(json.dumps(results))
    else:
        print(results)
