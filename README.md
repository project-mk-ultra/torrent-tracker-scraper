# Torrent Tracker Scraper

A UDP torrent tracker scraper written in Python 3 

![Coverage SVG](docs/imgs/coverage.svg)
[![PyPI version](https://badge.fury.io/py/torrent-tracker-scraper.svg)](https://badge.fury.io/py/torrent-tracker-scraper)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

<img src="docs/imgs/car-thief.jpg" width="400">

### Installation

```bash
pip install torrent-tracker-scraper
```

<img src="docs/imgs/thief-downloading-python-package.jpg" width="400">

## Usage

The package can be used either as a module within a script or straight up from the commandline.


<img src="docs/imgs/thief-tiptoe.jpg" width="400">

### As a python module
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


### Use it from the commandline

```bash
python3 -m torrent_tracker_scraper.scraper -i 95105D919C10E64AE4FA31067A8D37CCD33FE92D -t tracker.coppersurfer.tk -p 6969
```

**Outputs** 
```bash
Using tracker udp://tracker.coppersurfer.tk:6969
95105D919C10E64AE4FA31067A8D37CCD33FE92D, Seeds: 5045, Leechers: 742, Completed: 79802
```

#### Get JSON from the commandline

```bash
python3 -m torrent_tracker_scraper.scraper -i 95105D919C10E64AE4FA31067A8D37CCD33FE92D -t tracker.coppersurfer.tk -p 6969 -j
```

**Outputs**
```bash
{"infohash":"95105D919C10E64AE4FA31067A8D37CCD33FE92D","tracker":"udp://tracker.coppersurfer.tk:6969","seeders":171,"leechers":4,"completed":469}

```

<img src="docs/imgs/thief-with-an-early.2000s-limp-bizkit-cd.jpg" width="400">

### Testing

```bash
python -m unittest discover tests
```

![Thief Reviewing Unit Test Reports](docs/imgs/thief-reviewing-unit-test-reports.jpg)

### Help/Contributing

Use the normal GitHub bug reporting flow i.e Create an issue here 
<https://github.com/49e94b8f256530dc0d41f740dfe8a4c1/torrent-tracker-scraper/issues>.

Fork the code, make your changes and create a pull request.

### Behind the scenes

For a detailed quick rundown of whats going on behind the scenes

<https://blog.takeshispalace.com/programming/python3/udp/2018/12/23/udp-torrent-scraper-python.html>

### Contributors

<https://github.com/dessalines>


