import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="torrent-tracker-scraper",
    version="2.0.0",
    author="azerty",
    packages=['torrent_tracker_scraper'],
    author_email="kenokech94@gmail.com",
    description="A UDP torrent tracker scraper written in Python 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/49e94b8f256530dc0d41f740dfe8a4c1/torrent-tracker-scraper",
    # packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
    ),
    install_requires=[

    ],
)