# scrapy crawl doi_test_2 > output/final.links
import scrapy
import json
import psycopg2
import html

# import logging
# from scrapy.utils.log import configure_logging 

class IEEEX_Spider(scrapy.Spider):
    name = "doi_test_2"

    filename = 'output/links/x-artigos-2.links'
    start_urls = []
    with open(filename, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]


    ##############################################

    def parse(self, response):
        print(response.request.url)