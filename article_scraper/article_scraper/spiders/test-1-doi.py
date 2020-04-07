# scrapy crawl doi_test_1 > tests/1-venues/input/BD-final-artigos.links
import scrapy
import json
import psycopg2
import html


class IEEEX_Spider(scrapy.Spider):
    name = "doi_test_1"

    filename = 'tests/1-venues/input/BD-doi-artigos.links'
    start_urls = []
    with open(filename, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]

    ##############################################

    def parse(self, response):
        print(response.request.url)