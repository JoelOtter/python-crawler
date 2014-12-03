#!/usr/bin/env python
import time
import argparse
from crawl import Crawler


parser = argparse.ArgumentParser(
    description='Create a HTML site map from a domain.'
)
parser.add_argument('domain', help='The domain to be crawled')
parser.add_argument('-f', '--file',
                    help='self.output HTML file'
                    )
args = parser.parse_args()


class Parser:
    def __init__(self, tree, filename=False):
        self.tree = tree
        self.output_string = ""
        self.filename = filename

    def output(self, string, level):
        text = ' ' * level + string
        if args.file:
            self.output_string += text + '\n'
        else:
            print text

    def render_html(self, crawltime):
        self.output('Crawling: ' + args.domain, 0)
        self.output('<ul>', 0)
        self.print_tree(self.tree, 0)
        self.output('</ul>', 0)
        self.output('Crawled in ' + str(crawltime) + ' seconds.', 0)
        if self.filename:
            f = open(self.filename, 'w')
            f.write(self.output_string)
            f.close()
        else:
            print self.output_string

    def print_tree(self, tree, level):
        self.output('<li><a href="' + tree.url + '">' + tree.url + '</a></li>',
                    level)
        if tree.statics:
            self.output('<b>Static resources:</b>', level)
            self.output('<ul>', level)
            for s in tree.statics:
                self.output('<li>' + s[0] + ': <a href="' + s[1] +
                            '">' + s[1] + '</a></li>', level)
            self.output('</ul>', level)
        if tree.children:
            self.output('<b>Children:</b>', level)
            self.output('<ul>', level)
            for c in tree.children:
                self.print_tree(c, level + 1)
            self.output('</ul>', level)

starttime = time.time()
crawler = Crawler(args.domain)
c = crawler.crawl_domain()
endtime = time.time()
p = Parser(c, args.file)
p.render_html(endtime - starttime)
