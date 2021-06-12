from torrent_tracker_scraper import scraper

scraper = scraper.Scraper(
    # trackers=["udp//:camera.lei001.com:6969/announce"],
    infohashes=["FD55F8F6C08719D4D5E15EBF5EACEFBEC9ECE920",],
)
results = scraper.scrape()
print(results)
