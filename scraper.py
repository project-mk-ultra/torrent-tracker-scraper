# !/usr/bin/env python
# scrape.py
import binascii
import socket
import struct
import argparse
from random import randrange  # to generate random transaction_id

from utils import Utils

# the most stable tracker known out there
UDP_TRACKER = "tracker.coppersurfer.tk"
# the default OpenTracker port
UDP_PORT = 6969
# random West World episodes
torrent_hash = ["95105D919C10E64AE4FA31067A8D37CCD33FE92D",
                "37AFFEA745D2193348"]


def scrape(infohash):
    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((UDP_TRACKER, UDP_PORT))

    # Protocol says to keep it that way
    protocol_id = 0x41727101980

    # We should get the same in response
    transaction_id = randrange(1, 65535)

    # Connection request
    packet = struct.pack(">QLL", protocol_id, 0, transaction_id)
    sock.send(packet)

    # Connection response
    res = sock.recv(16)
    action, transaction_id, connection_id = struct.unpack(">LLQ", res)

    packet_hashes = str()
    if not Utils.is_40_char_long(infohash):
        print("Skipping infohash {0}".format(infohash))
        sock.close()
        return "Invalid infohash {0}".format(infohash)
    packet_hashes = bytearray(packet_hashes, 'utf-8') + binascii.unhexlify(infohash)

    # Scrape requests
    packet = struct.pack(">QLL", connection_id, 2, transaction_id) + packet_hashes
    sock.send(packet)

    # Scrape response
    res = sock.recv(8 + 12 * len(torrent_hash))

    index = 8
    seeders, completed, leechers = struct.unpack(">LLL", res[index:index + 12])
    print("{3} Seeds: {0}, Leechers: {1}, Completed: {2}".format(seeders, leechers, completed, infohash))
    index = index + 12

    # close the socket, job is done.
    sock.close()

    return infohash, seeders, leechers, completed


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
    args, unknown = parser.parse_known_args()
    scrape(args.infohash)
