# scrapy crawl dblp_venue > output/x-venues.links
import scrapy

import json
import requests
import logging

from bs4 import BeautifulSoup
from lxml import html
from pymongo import MongoClient
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class DBLP_Venue_Spider(scrapy.Spider):
    name = "dblp_venue"

    start_urls = [
        # 'https://dblp.org/db/conf/sigir/',
    ]
    # filepath = 'tests/1-venues/IHC-links/dl-acm-org-2.links'
    # with open(filepath, "r") as f:
    #     start_urls = [url.strip() for url in f.readlines()]
    # start_urls = list(filter(lambda url: not 'proceedings' in url, start_urls))

    # ======= Links =======

    def extract_dblp_links(self, response):
        xpath_string = "//li/a[not(@class) and contains(@href, 'https://dblp.org/') and @itemprop='url']/@href"
        links = response.xpath(xpath_string).getall()

        if (links == []):
            xpath_string = "//li/a[contains(@href, '//dblp.org/')]/@href"
            links = response.xpath(xpath_string).getall()

        return links

    ##############################################

    def remove_tags(self, string):
        return BeautifulSoup(string, "lxml").text
    
    ##############################################

    def parse(self, response):
        links = self.extract_dblp_links(response)
        # print(response.request.url)
        for l in links:
            print(l)