### Torrent Tracker Scraper

A UDP torrent tracker scraper written in Python 3 

[![PyPI version](https://badge.fury.io/py/torrent-tracker-scraper.svg)](https://badge.fury.io/py/torrent-tracker-scraper)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

### Usage

#### As a python module
```python
from torrent_tracker_scraper import scraper

torrent_infohash, seeders, leechers, complete = scraper.scrape(
                "95105D919C10E64AE4FA31067A8D37CCD33FE92D",
                "tracker.coppersurfer.tk",
                6969
            )
            
print(torrent_infohash)
```

Outputs 

```bash
Using tracker udp://tracker.coppersurfer.tk:6969
(95105D919C10E64AE4FA31067A8D37CCD33FE92D, 5045, 742, 79802) 
# it returns a tuple with (infohash, seeders, leechers, completed)
```


#### As a CLI program

```bash
python3 -m torrent_tracker_scraper.scraper -i 95105D919C10E64AE4FA31067A8D37CCD33FE92D -t tracker.coppersurfer.tk -p 6969
```

Outputs 
```bash
Using tracker udp://tracker.coppersurfer.tk:6969
95105D919C10E64AE4FA31067A8D37CCD33FE92D, Seeds: 5045, Leechers: 742, Completed: 79802
```

### Setup

```bash
pip install torrent-tracker-scraper
```

### Help/Contributing

Use the normal Github bug reporting flow i.e Create an issue here 
<https://github.com/ZigmundVonZaun/torrent-tracker-scraper/issues>.

Fork the code, make your changes and create a pull request.

Send me an email <ziggs@airmail.cc> for any queries.
 
I'll get back to you in a couple of hours at most.


### Behind the scenes

For a detailed quick rundown of whats going on behind the scenes

<https://districtofzaun.info/python/programming/torrents/2018/04/05/scraping-udp-trackers-using-python>
