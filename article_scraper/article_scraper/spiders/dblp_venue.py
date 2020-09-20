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
        'https://dblp.org/db/conf/gis/',
        'https://dblp.org/db/conf/sac/',
        'https://dblp.org/db/conf/cloud/',
        'https://dblp.org/db/journals/tods/',
        'https://dblp.org/db/journals/tois/',
        'https://dblp.org/db/journals/tist/',
        'https://dblp.org/db/journals/tweb/',
        'https://dblp.org/db/conf/adbis/',
        'https://dblp.org/db/conf/amw/',
        'https://dblp.org/db/conf/apweb/',
        'https://dblp.org/db/conf/er/',
        'https://dblp.org/db/conf/dexa/',
        'https://dblp.org/db/conf/chiir/',
        'https://dblp.org/db/journals/datamine/',
        'https://dblp.org/db/conf/date/',
        'https://dblp.org/db/journals/dpd/',
        'https://dblp.org/db/conf/esws/',
        'https://dblp.org/db/conf/ecir/',
        'https://dblp.org/db/journals/geoinformatica/',
        'https://dblp.org/db/conf/cbms/',
        'https://dblp.org/db/conf/civts/',
        'https://dblp.org/db/conf/aina/',
        'https://dblp.org/db/conf/bigdataconf/',
        'https://dblp.org/db/conf/icde/',
        'https://dblp.org/db/conf/icdm/',
        'https://dblp.org/db/conf/mdm/',
        'https://dblp.org/db/conf/ucc/',
        'https://dblp.org/db/conf/eScience/',
        'https://dblp.org/db/conf/ism/',
        'https://dblp.org/db/conf/mm/',
        'https://dblp.org/db/journals/tr/',
        'https://dblp.org/db/journals/tii/ ',
        'https://dblp.org/db/journals/tkde/',
        'https://dblp.org/db/journals/tmm/',
        'https://dblp.org/db/conf/pts/',
        'https://dblp.org/db/conf/sigir/',
        'https://dblp.org/db/conf/caise/',
        'https://dblp.org/db/conf/coopis/',
        'https://dblp.org/db/conf/dawak/',
        'https://dblp.org/db/conf/iiwas/',
        'https://dblp.org/db/conf/mtsr/',
        'https://dblp.org/db/conf/ssdbm/',
        'https://dblp.org/db/conf/ictir/',
        'https://dblp.org/db/conf/wise/',
        'https://dblp.org/db/conf/ideas/',
        'https://dblp.org/db/conf/ipaw/',
        'https://dblp.org/db/conf/ssd/',
        'https://dblp.org/db/conf/dolap/dolap2013.html',
        'https://dblp.org/db/conf/webdb/',
        'https://dblp.org/db/conf/www/',
        'https://dblp.org/db/journals/grid/',
        'https://dblp.org/db/journals/jiis/',
        'https://dblp.org/db/journals/mms/',
        'https://dblp.org/db/journals/mta/',
        'https://dblp.org/db/conf/pakdd/',
        'https://dblp.org/db/journals/sigmod/',
        'https://dblp.org/db/conf/cidm/',
        'https://dblp.org/db/conf/pods/',
        'https://dblp.org/db/journals/vldb/',
        'https://dblp.org/db/journals/algorithmica/'
    ]
    # filepath = 'tests/1-venues/IHC-links/dl-acm-org-2.links'
    # with open(filepath, "r") as f:
    #     start_urls = [url.strip() for url in f.readlines()]
    # start_urls = list(filter(lambda url: not 'proceedings' in url, start_urls))

    # ======= Links =======

    def extract_dblp_links(self, response):
        links = []
        # xpath_string = "//li/a[not(@class) and contains(@href, 'https://dblp.org/') and @itemprop='url']/@href",
        # links = response.xpath(xpath_string).getall()

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
        print('Link:', response.request.url)
        for l in links:
            print(l)
        print('##############################################')