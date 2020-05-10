# Torrent Tracker Scraper

A UDP torrent tracker scraper written in Python 3

![Jenkins](https://jenkins.psr42.online/job/torrent-tracker-scraper/badge/icon?)
[![PyPI version](https://badge.fury.io/py/torrent-tracker-scraper.svg)](https://badge.fury.io/py/torrent-tracker-scraper)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

<img src="docs/imgs/car-thief.jpg" width="400">

## Installation

```bash
pipenv install torrent-tracker-scraper
pipenv shell
```

<img src="docs/imgs/thief-downloading-python-package.jpg" width="400">

## Usage

The package can be used either as a module within a script or straight up from the commandline.

Pass in a single infohash

```python
from torrent_tracker_scraper import scraper

scraper = scraper.Scraper("tracker.coppersuffer.tk", 6969, json=True)

results = scraper.scrape("95105D919C10E64AE4FA31067A8D37CCD33FE92D")
print(results)

{'tracker': 'tracker.coppersuffer.tk', 'results': [{'infohash': '95105D919C10E64AE4FA31067A8D37CCD33FE92D', 'seeders': 112, 'completed': 496, 'leechers': 2}]}
```

pass in multiple infohashes separated by commas

```python
results = scraper.scrape("95105D919C10E64AE4FA31067A8D37CCD33FE92D,913EF55D5DD1A9376B738922E5104B3A1BE3754A")
print(results)

{'tracker': 'tracker.coppersuffer.tk', 'results': [{'infohash': '95105D919C10E64AE4FA31067A8D37CCD33FE92D', 'seeders': 112, 'completed': 496, 'leechers': 2}, {'infohash': '913EF55D5DD1A9376B738922E5104B3A1BE3754A', 'seeders': 334, 'completed': 989, 'leechers': 250}]}
```

pass in a list of infohashes

```python
results = scraper.scrape(["913EF55D5DD1A9376B738922E5104B3A1BE3754A", "95105D919C10E64AE4FA31067A8D37CCD33FE92D"])
print(results)

{'tracker': 'tracker.coppersuffer.tk', 'results': [{'infohash': '913EF55D5DD1A9376B738922E5104B3A1BE3754A', 'seeders': 334, 'completed': 989, 'leechers': 250}, {'infohash': '95105D919C10E64AE4FA31067A8D37CCD33FE92D', 'seeders': 112, 'completed': 496, 'leechers': 2}]}
```

Get your scrapped information

<img src="docs/imgs/thief-with-an-early.2000s-limp-bizkit-cd.jpg" width="400">

### Testing

```bash
pipenv install --dev
pipenv shell
python -m pytest
```

<img src="docs/imgs/thief-reviewing-unit-test-reports.jpg" width="400">

### Help/Contributing

Use the normal GitHub bug reporting flow i.e Create an issue here
<https://github.com/49e94b8f256530dc0d41f740dfe8a4c1/torrent-tracker-scraper/issues>.

Fork the code, make your changes and create a pull request.

### Behind the scenes

For a detailed quick rundown of whats going on behind the scenes

<https://blog.takeshispalace.com/programming/python3/udp/2018/12/23/udp-torrent-scraper-python.html>

<img src="docs/imgs/thief-tiptoe.jpg" width="400">

### Contributors

<https://github.com/dessalines>
