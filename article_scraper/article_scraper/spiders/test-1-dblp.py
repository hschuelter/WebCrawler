# scrapy crawl doi_dblp_1 > tests/1-venues/input/IHC-doi-artigos.links
import scrapy
import json
import psycopg2
import html


class IEEEX_Spider(scrapy.Spider):
    name = "doi_dblp_1"

    filepath = 'tests/1-venues/input/journal-url-ihc.txt'
    start_urls = []
    with open(filepath, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]

    ##############################################

    def parse(self, response):
        xpath_string = "//li[@class='ee']/a/@href"
        links = response.xpath(xpath_string).getall()
        for l in links:
            if('doi.org' in l):
                print(l)
