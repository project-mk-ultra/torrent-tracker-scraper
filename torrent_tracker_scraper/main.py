import argparse
import logging

from torrent_tracker_scraper.scraper import Scraper
from torrent_tracker_scraper.utils import Utils

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
    scraper = Scraper(args.tracker, args.port, args.json, args.timeout)
    scraper.scrape(args.infohash)
