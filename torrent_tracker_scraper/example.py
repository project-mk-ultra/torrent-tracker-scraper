import scraper

if __name__ == "__main__":
    scraper = scraper.Scraper(
        # trackers=["udp://bt2.archive.org:6969"],
        infohashes=[
            "73C36F980F5B1A40348678036575CCC1E0BB0E4E",
            "52AFB643744CD57030763420D7D2B45BF4D8D2D3",
        ],
        timeout=1,
    )
    results = scraper.scrape()
    # print("results", results)
    for result in results:
        # print(result)
        if isinstance(result, list):
            print(result)

    # scraper = scraper.Scraper(infohashes=['82026E5C56F0AEACEDCE2D7BC2074A644BC50990', '04D9A2D3FAEA111356519A0E0775E5EAEE9C944A'])
    # results = scraper.scrape()
    # for result in results:
    #     print(result)

    # import scraper

    # scraper = scraper.Scraper(
    #     trackers=['udp://explodie.org:6969/announce'],
    #     infohashes=['82026E5C56F0AEACEDCE2D7BC2074A644BC50990', '04D9A2D3FAEA111356519A0E0775E5EAEE9C944A'])
    # results = scraper.scrape()
    # for result in results:
    #     print(result)
