# !/usr/bin/env python
# scrape.py
import argparse
import binascii
import logging
import os
import random
import socket
import struct
from threading import Timer

from torrent_tracker_scraper.utils import Utils

# setup Logging

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)


def connect(hostname, port):
    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # connect socket
        sock.connect((hostname, port))
    except:
        # handle socket connection error
        logging.warning(
            "Tracker udp://{0}:{1} down falling back to udp://tracker.coppersurfer.tk".format(hostname, port))
        try:
            sock.connect(("tracker.coppersurfer.tk", 6969))
            return sock
        except Exception as e:
            sock.close()
            logging.error(e)
            logging.error(" Tracker udp://{0}:{1} is also down, check your Internet".format("tracker.coppersurfer.tk",
                                                                                            6969))
            return None
    return sock


def scrape(infohash, tracker_hostname, tracker_port, json=False, timeout=5):
    """
    Takes in an infohash, tracker hostname and listening port. Returns seeders, leechers and completed
    information
    :param infohash: SHA-1 representation of the ```info``` key in the torrent file
    :param tracker_hostname: Hostname of the UDP tracker. The hostname without the scheme.
    :param tracker_port: Listening port of the UDP tracker
    :param json: If output should be JSON
    :param timeout  Scraper timeout
    :return: infohash, seeders, leechers, completed
    """
    tracker_udp = "udp://{0}:{1}".format(tracker_hostname, tracker_port)

    # Start a timer
    timer = Timer(timeout, exit_program)
    timer.start()

    # Create the socket
    sock = connect(tracker_hostname, tracker_port)
    if sock is None:
        return "Tracker {0} is down".format(tracker_udp)

    # Protocol says to keep it that way
    protocol_id = 0x41727101980

    # We should get the same in response
    transaction_id = random.randrange(1, 65535)

    # Connection request
    packet = struct.pack(">QLL", protocol_id, 0, transaction_id)
    sock.send(packet)

    # Connection response
    res = sock.recv(16)
    action, transaction_id, connection_id = struct.unpack(">LLQ", res)

    packet_hashes = str()
    if not Utils.is_40_char_long(infohash):
        logging.warning("Skipping infohash {0}".format(infohash))
        sock.close()
        return "Invalid infohash {0}".format(infohash)
    packet_hashes = bytearray(packet_hashes, 'utf-8') + binascii.unhexlify(infohash)

    # Scrape requests
    packet = struct.pack(">QLL", connection_id, 2, transaction_id) + packet_hashes
    sock.send(packet)

    # Scrape response
    res = sock.recv(8 + 12 * len(infohash))

    index = 8
    seeders, completed, leechers = struct.unpack(">LLL", res[index:index + 12])
    if (json):
        logging.info(
            "{{\"infohash\":\"{3}\",\"tracker\":\"{4}\",\"seeders\":{0},\"leechers\":{1},\"completed\":{2}}}".format(
                seeders, leechers, completed, infohash, tracker_udp))
    else:
        logging.info("Using tracker {0}".format(tracker_udp))
        logging.info("{3} Seeds: {0}, Leechers: {1}, Completed: {2}".format(seeders, leechers, completed, infohash))

    index = index + 12

    # close the socket, job is done.
    sock.close()
    timer.cancel()

    return infohash, seeders, leechers, completed


def exit_program():
    print("Tracker timed out")
    os._exit(1)


if __name__ == "__main__":
    def check_infohash(value):
        if not Utils.is_40_char_long(value):
            raise argparse.ArgumentTypeError('Infohash is not valid')
        else:
            return value


    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--infohash",
                        help="A torrents infohash or a file path consisting of infohashes",
                        type=check_infohash,
                        default="95105D919C10E64AE4FA31067A8D37CCD33FE92D")
    parser.add_argument("-t",
                        "--tracker",
                        help="Entered in the format :tracker",
                        type=str,
                        default="tracker.coppersurfer.tk")
    parser.add_argument("-p",
                        "--port",
                        help="Entered in the format :port",
                        type=int,
                        default=6969)
    parser.add_argument("-j",
                        "--json",
                        help="Output in json format",
                        dest='json',
                        action='store_true')
    parser.add_argument("-to",
                        "--timeout",
                        help="Enter the timeout in seconds",
                        type=int,
                        default=5)
    parser.set_defaults(json=False)

    args, unknown = parser.parse_known_args()
    scrape(args.infohash, args.tracker, args.port, args.json, args.timeout)
