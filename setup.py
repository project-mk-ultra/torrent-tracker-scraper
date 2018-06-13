import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="torrent-tracker-scraper",
    version="0.0.8",
    author="ziggs",
    packages=['torrent_tracker_scraper'],
    author_email="ziggs@airmail.cc",
    description="A UDP torrent tracker scraper written in Python 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZigmundVonZaun/torrent-tracker-scraper",
    # packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
    ),
)