# !/usr/bin/env python
# scrape.py
import binascii
import json
import logging
import os
import random
import struct
from threading import Timer

from torrent_tracker_scraper.connection import Connection
from torrent_tracker_scraper.mylogger import MyLogger
from torrent_tracker_scraper.utils import Utils


class Scraper:
    def __init__(self, hostname, port, json=False, timeout=15):
        """
        Launches a scraper bound to a particular tracker
        :param hostname: Tracker hostname e.g. coppersuffer.tk
        :param port: 6969, self-explanatory
        :param json: dictates if a json object should be returned as the output
        :param timeout: Timeout value in seconds, program exits if no response received within this period
        """
        self.json = json
        self.timeout = timeout
        self.connection = Connection(hostname, port)

    def scrape(self, infohashes):
        """
        Takes in an infohash, tracker hostname and listening port. Returns seeders, leechers and completed
        information
        :param infohashes: SHA-1 representation of the ```info``` key in the torrent file
        :return: [(infohash, seeders, leechers, completed),...]
        """

        tracker_url = "udp://{0}:{1}".format(self.connection.hostname, self.connection.port)

        # Start a timer
        timer = Timer(self.timeout, exit_program)
        timer.start()

        # quit scraping if there is no connection
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

        # if infohashes is a string
        if isinstance(infohashes, str):
            # check if it is a single infohash
            if "," not in infohashes:
                MyLogger.log("Parsing single string infohash", logging.DEBUG)
                # Validate if string is actually an infohash
                if not Utils.is_40_char_long(infohashes):
                    logging.warning("Skipping infohash {0}".format(infohashes))
                    return "Invalid infohash {0}, skipping".format(infohashes)
                packet_hashes = bytearray(str(), 'utf-8')
                packet_hashes += binascii.unhexlify(infohashes)

                # Send Scrape Request
                packet = struct.pack(">QLL", connection_id, 2, transaction_id) + packet_hashes
                self.connection.sock.send(packet)

                # Receive Scrape Response
                res = self.connection.sock.recv(8 + 12 * len(infohashes))

                index = 8
                seeders, completed, leechers = struct.unpack(">LLL", res[index:index + 12])
                results.append(
                    {"infohash": infohashes, "seeders": seeders, "completed": completed, "leechers": leechers})

            else:
                # multiple infohashes separated by a comma
                MyLogger.log("Parsing multiple string infohashes", logging.DEBUG)
                infohashes = infohashes.split(",")
                packet_hashes = bytearray(str(), 'utf-8')
                for i, infohash in enumerate(infohashes):
                    packet_hashes += binascii.unhexlify(infohash)
                packet = struct.pack(">QLL", connection_id, 2, transaction_id) + packet_hashes
                self.connection.sock.send(packet)

                # Scrape response
                res = self.connection.sock.recv(8 + (12 * len(infohashes)))

                index = 8
                for i in range(1, len(infohashes) + 1):
                    MyLogger.log("Offset: {} {}".format(index + (i * 12) - 12, index + (i * 12)), logging.DEBUG)
                    seeders, completed, leechers = struct.unpack(">LLL", res[index + (i * 12) - 12: index + (i * 12)])
                    results.append({"infohash": infohashes[i - 1],
                                    "seeders": seeders,
                                    "completed": completed,
                                    "leechers": leechers})
        elif isinstance(infohashes, list):
            MyLogger.log("Parsing list of infohashes", logging.DEBUG)
            packet_hashes = bytearray(str(), 'utf-8')
            for i, infohash in enumerate(infohashes):
                packet_hashes += binascii.unhexlify(infohash)
            packet = struct.pack(">QLL", connection_id, 2, transaction_id) + packet_hashes
            self.connection.sock.send(packet)

            # Scrape response
            res = self.connection.sock.recv(8 + (12 * len(infohashes)))

            index = 8
            for i in range(1, len(infohashes) + 1):
                MyLogger.log("Offset: {} {}".format(index + (i * 12) - 12, index + (i * 12)), logging.DEBUG)
                seeders, completed, leechers = struct.unpack(">LLL", res[index + (i * 12) - 12: index + (i * 12)])
                results.append({"infohash": infohashes[i - 1],
                                "seeders": seeders,
                                "completed": completed,
                                "leechers": leechers})

        timer.cancel()
        results = {"tracker": f'{self.connection.hostname}:{self.connection.port}', "results": results}
        return results

    def __del__(self):
        """
        Close connection if the scraper object is being destroyed
        :return: None
        """
        self.connection.close()

    def __repr__(self):
        return f'{self.connection.hostname}:{self.connection.port}'


def exit_program():
    print("Tracker timed out")
    os._exit(1)
