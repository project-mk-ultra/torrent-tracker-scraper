if __name__ == '__main__':
    import scraper

    scraper = scraper.Scraper(infohashes=['82026E5C56F0AEACEDCE2D7BC2074A644BC50990', '04D9A2D3FAEA111356519A0E0775E5EAEE9C944A'])
    results = scraper.scrape()
    for result in results:
        print(result)

    import scraper

    scraper = scraper.Scraper(
        trackers=['udp://explodie.org:6969/announce'], 
        infohashes=['82026E5C56F0AEACEDCE2D7BC2074A644BC50990', '04D9A2D3FAEA111356519A0E0775E5EAEE9C944A'])
    results = scraper.scrape()
    for result in results:
        print(result)