# scrapy crawl doi-test-0 > tests/0-interaction/final-artigos.links
import scrapy
import json
import psycopg2
import html


class IEEEX_Spider(scrapy.Spider):
    name = "doi-test-0"

    filename = 'tests/0-interaction/artigos.links'
    start_urls = []
    with open(filename, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]

    ##############################################

    def parse(self, response):
        print(response.request.url)