# Torrent Tracker Scraper

A UDP torrent tracker scraper written in Python 3

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/torrent-tracker-scraper.svg)](https://pypi.python.org/pypi/torrent-tracker-scraper/)
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

### Pass in a list of infohashes

```python
from torrent_tracker_scraper import scraper

scraper = scraper.Scraper(
    infohashes=[
        "82026E5C56F0AEACEDCE2D7BC2074A644BC50990",
        "04D9A2D3FAEA111356519A0E0775E5EAEE9C944A",
    ]
)
results = scraper.scrape()
print(results)

[
    ...,
    {
        'tracker': 'udp://explodie.org:6969',
        'results': [
            {
                'infohash': '82026E5C56F0AEACEDCE2D7BC2074A644BC50990',
                'seeders': 246,
                'completed': 0,
                'leechers': 36
            },
            {
                'infohash': '04D9A2D3FAEA111356519A0E0775E5EAEE9C944A',
                'seeders': 7,
                'completed': 0,
                'leechers': 27
            }
        ]
    },
    ...
```

Get your scrapped information

<img src="docs/imgs/thief-with-an-early.2000s-limp-bizkit-cd.jpg" width="400">

### Pass in a list of trackers

```python
from torrent_tracker_scraper import scraper

scraper = scraper.Scraper(
    trackers=["udp://explodie.org:6969/annouce"],
    infohashes=[
        "82026E5C56F0AEACEDCE2D7BC2074A644BC50990",
        "04D9A2D3FAEA111356519A0E0775E5EAEE9C944A",
    ],
)
results = scraper.scrape()
print(results)

[
    ...,
    {
        'tracker': 'udp://explodie.org:6969',
        'results': [
            {
                'infohash': '82026E5C56F0AEACEDCE2D7BC2074A644BC50990',
                'seeders': 246,
                'completed': 0,
                'leechers': 36
            },
            {
                'infohash': '04D9A2D3FAEA111356519A0E0775E5EAEE9C944A',
                'seeders': 7,
                'completed': 0,
                'leechers': 27
            }
        ]
    },
    ...
```

## Testing

```bash
pipenv install --dev
pipenv run pytest
```

<img src="docs/imgs/thief-reviewing-unit-test-reports.jpg" width="400">

## Help/Contributing

1. Install dev dependencies `pipenv install --dev`

2. Make your changes

3. Make sure your tests pass `pipenv run pytest`

4. Create an issue here

   <https://github.com/project-mk-ultra/torrent-tracker-scraper/issues>.

   <img src="docs/imgs/thief-tiptoe.jpg" width="400">

## Contributors (in alphabetical order)

1. <https://github.com/49e94b8f256530dc0d41f740dfe8a4c1>
2. <https://github.com/dessalines>
3. <https://github.com/zawi99>
