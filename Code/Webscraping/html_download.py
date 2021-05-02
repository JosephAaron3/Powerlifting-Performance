"""Webscraper for downloading .html pages for a list of links."""

import urllib
from tqdm import tqdm

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
       Chrome/41.0.2228.0 Safari/537.3'}
BASE_LINK = "https://powerliftingaustralia.com/wp-content/uploads/results/"


def html_download(url):
    req = urllib.request.Request(url=url, headers=HDR)
    page = urllib.request.urlopen(req).read()
    with open('../Data/Pages/' + url[len(BASE_LINK):].replace('/', ''), 'wb') as f:
        f.write(page)


with open('../Data/PowerliftingCompLinks.csv', 'r') as f:
    count = 0
    for link in tqdm(f):
        count += 1
        try:
            html_download(link.strip('\n'))
        except Exception:
            continue
