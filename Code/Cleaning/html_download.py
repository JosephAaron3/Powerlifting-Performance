import urllib
import csv
from bs4 import BeautifulSoup as soup
from tqdm import tqdm

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
base_link = "https://powerliftingaustralia.com/wp-content/uploads/results/"

def HTML_download(url):
    req = urllib.request.Request(url=url, headers=hdr) 
    page = urllib.request.urlopen(req).read() 
    with open('../Data/Pages/' + url[len(base_link):].replace('/',''), 'wb') as f:
        f.write(page)

if __name__ == "__main__":
    with open('../Data/PowerliftingCompLinks.csv','r') as f:
        count = 0
        for link in tqdm(f):
            count += 1
            try:
                HTML_download(link.strip('\n'))
            except(Exception):
                continue