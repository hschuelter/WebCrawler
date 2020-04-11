# scrapy crawl doi_test_1 > tests/1-venues/input/IHC-final-artigos-2.links
import scrapy
import json
import psycopg2
import html

import logging


class IEEEX_Spider(scrapy.Spider):
    name = "doi_test_1"

    filename = 'tests/1-venues/input/ihc/IHC-doi-artigos.links'
    start_urls = []
    with open(filename, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]

    log_file = 'tests/1-venues/input/IHC-final-artigos.log'
    logging.basicConfig(filename=log_file,level=logging.DEBUG)

    ##############################################

    def parse(self, response):
        print(response.request.url)