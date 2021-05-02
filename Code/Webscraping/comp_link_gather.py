"""Webscraper for getting HTML links to all competition tables."""

import urllib
import csv
from bs4 import BeautifulSoup as soup

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
           Chrome/41.0.2228.0 Safari/537.3'}
BASE_LINK = "https://powerliftingaustralia.com/wp-content/uploads/results/"


def search_link_parser(url):
    req = urllib.request.Request(url=url, headers=HDR)
    page = urllib.request.urlopen(req).read()
    content = soup(page, 'html.parser')
    links = content.find_all(name='a')
    return [link.get('href') for link in links]


count = 0
years = list(range(2000, 2022))
urls = {year: search_link_parser(BASE_LINK + str(year)) for year in years}
with open('../Data/PowerliftingCompLinks.csv', 'a', newline='') as fd:
    writer = csv.writer(fd)
    for year, links in urls.items():
        for link in links:
            if ".htm" in link:
                writer.writerow([BASE_LINK + str(year) + "/" + str(link)])
                count += 1
print("Found", count, "links")
