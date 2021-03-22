import urllib
import csv
from bs4 import BeautifulSoup as soup

def SearchLinkParser(url):
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = urllib.request.Request(url=url, headers=hdr) 
    page = urllib.request.urlopen(req).read() 
    content = soup(page, 'html.parser')
    links = content.find_all(name = 'a')
    return [link.get('href') for link in links]

if __name__ == "__main__":
    count = 0
    years = list(range(2000,2022))
    base_link = "https://powerliftingaustralia.com/wp-content/uploads/results/"
    urls = {year: SearchLinkParser(base_link+str(year)) for year in years}
    with open('../Data/PowerliftingCompLinks.csv','a',newline='') as fd:
        writer = csv.writer(fd)
        for year,links in urls.items():
            for link in links:
                if ".htm" in link:
                    writer.writerow([base_link+str(year)+str(link)])
                    count += 1
    print("Found", count, "links")