# !/usr/bin/env python
# scrape.py
import binascii
import logging
import os
import random
import struct
from threading import Timer

from torrent_tracker_scraper.connection import Connection
from torrent_tracker_scraper.mylogger import MyLogger
from torrent_tracker_scraper.utils import Utils


class Scraper:
    def __init__(self, hostname, port, json, timeout=15):
        self.json = json
        self.timeout = timeout
        self.connection = Connection(hostname, port)

    def scrape(self, infohashes):
        """
        Takes in an infohash, tracker hostname and listening port. Returns seeders, leechers and completed
        information
        :param infohashes: SHA-1 representation of the ```info``` key in the torrent file
        :param hostname: Hostname of the UDP tracker. The hostname without the scheme.
        :param port: Listening port of the UDP tracker
        :param json: If output should be JSON
        :param timeout  Scraper timeout
        :return: infohash, seeders, leechers, completed
        """

        tracker_udp_url = "udp://{0}:{1}".format(self.connection.hostname, self.connection.port)

        # Start a timer
        timer = Timer(self.timeout, exit_program)
        timer.start()

        # quit scraping if there is no connection
        if self.connection.sock is None:
            return "Tracker {0} is down".format(tracker_udp_url)

        # Protocol says to keep it that way
        protocol_id = 0x41727101980

        # We should get the same in response
        transaction_id = random.randrange(1, 65535)

        # Send a Connect Request
        packet = struct.pack(">QLL", protocol_id, 0, transaction_id)
        self.connection.sock.send(packet)

        # Connect Request response
        res = self.connection.sock.recv(16)
        action, transaction_id, connection_id = struct.unpack(">LLQ", res)

        # if infohashes is a string
        if isinstance(infohashes, str):
            # check if it is a single infohash
            if "," not in infohashes:
                if not Utils.is_40_char_long(infohashes):
                    logging.warning("Skipping infohash {0}".format(infohashes))
                    self.connection.sock.close()
                    return "Invalid infohash {0}".format(infohashes)
                packet_hashes = bytearray(str(), 'utf-8')
                packet_hashes += binascii.unhexlify(infohashes)

                # Send Scrape Request
                packet = struct.pack(">QLL", connection_id, 2, transaction_id) + packet_hashes
                self.connection.sock.send(packet)

                # Receive Scrape Response
                res = self.connection.sock.recv(8 + 12 * len(infohashes))

                index = 8
                seeders, completed, leechers = struct.unpack(">LLL", res[index:index + 12])
                if self.json:
                    MyLogger.log(
                        "{{\"infohash\":\"{3}\",\"tracker\":\"{4}\",\"seeders\":{0},\"leechers\":{1},\"completed\":{"
                        "2}}}".format(
                            seeders, leechers, completed, infohashes, tracker_udp_url), logging.INFO)
                else:
                    MyLogger.log("Using tracker {0}".format(tracker_udp_url), logging.INFO)
                    MyLogger.log("{3} Seeds: {0}, Leechers: {1}, Completed: {2}".format(seeders, leechers, completed,
                                                                                        infohashes),
                                 logging.INFO)

                index = index + 12

                # close the socket, job done.
                self.connection.close()
                timer.cancel()

                return infohashes, seeders, leechers, completed
            else:
                # multiple infohashes separated by a comma
                infohashes = infohashes.split(",")
                MyLogger.log(infohashes, logging.INFO)
                packet_hashes = bytearray(str(), 'utf-8')
                for i, infohash in enumerate(infohashes):
                    packet_hashes += binascii.unhexlify(infohash)
                packet = struct.pack(">QLL", connection_id, 2, transaction_id) + packet_hashes
                self.connection.sock.send(packet)

                # Scrape response
                res = self.connection.sock.recv(8 + (12 * len(infohashes)))

                index = 8
                for i in range(1, len(infohashes)+1):
                    seeders, completed, leechers = struct.unpack(">LLL", res[index: index + (i * 12)])
                    MyLogger.log("{} {} {}".format(seeders, completed, seeders), logging.INFO)


def exit_program():
    print("Tracker timed out")
    os._exit(1)
