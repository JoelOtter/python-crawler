import requests
import re
import threading
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup


class CrawlerPage:
    def __init__(self, url):
        self.url = url
        self.children = []
        self.statics = []


class Crawler:
    def __init__(self, domain):
        self.domain = domain
        self.seen_urls = []
        self.seen_lock = threading.Lock()

    def _get_page_url(self, link_url):
        absolute_url = re.match(r'^(https?://(.+\.)?' + self.domain
                                + r'[\-_A-Za-z0-9\.]*)\??.*$', link_url)
        relative_url = re.match(r'^(/[/\-_A-Za-z0-9\.]+)', link_url)

        if absolute_url:
            return absolute_url.group(1)
        elif relative_url:
            return 'http://www.' + self.domain + relative_url.group(1)

    def _get_static_url(self, link_url, page_url):
        absolute_url = re.match(r'^(https?://[/\-_A-Za-z0-9\.@]+)\??.*$',
                                link_url)
        domain_rel_url = re.match(r'^(/[/\-_A-Za-z0-9\.@]+)\??.*$', link_url)
        relative_url = re.match(r'^([^/][/\-_A-Za-z0-9\.@]+)\??.*$', link_url)
        twoslash_url = re.match(r'^(//[/\-_A-Za-z0-9\.@]+)\??.*$', link_url)
        if absolute_url:
            return absolute_url.group(1)
        elif twoslash_url:
            return 'http:' + twoslash_url.group(1)
        elif domain_rel_url:
            return 'http://www.' + self.domain + domain_rel_url.group(1)
        elif relative_url:
            return page_url + '/' + relative_url.group(1)

    def _get_children_from_links(self, links):
        children = []
        for link in links:
            link_url = link.get('href')
            if not link_url:
                continue
            page_url = self._get_page_url(link_url)
            with self.seen_lock:
                if page_url and page_url not in self.seen_urls:
                    self.seen_urls.append(page_url)
                    children.append(CrawlerPage(page_url))
        return children

    def _get_statics_from_soup(self, soup, page_url):
        statics = []

        tags = soup.find_all(['img', 'script', 'link'])
        for t in tags:
            src = t.get('src')
            datasrc = t.get('data-src')
            href = t.get('href')
            stat_url = None
            if src:
                stat_url = self._get_static_url(src, page_url)
            elif href and t.name == 'link' and 'stylesheet' in t.get('rel'):
                stat_url = self._get_static_url(href, page_url)
            elif datasrc and t.name == 'img':
                stat_url = self._get_static_url(datasrc, page_url)

            if stat_url:
                if t.name == 'link':
                    statics.append(('stylesheet', stat_url))
                else:
                    statics.append((t.name, stat_url))

        return statics

    def crawl(self, page):
        try:
            html = requests.get(page.url).text
        except requests.ConnectionError:
            return
        soup = BeautifulSoup(html)
        page.children = self._get_children_from_links(soup.find_all('a'))
        page.statics = self._get_statics_from_soup(soup, page.url)

        pool = Pool()
        pool.map(self.crawl, page.children)
        pool.close()
        pool.join()
        return page

    def crawl_domain(self):
        return self.crawl(CrawlerPage('http://www.' + self.domain))
