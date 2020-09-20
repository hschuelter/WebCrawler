# scrapy crawl dblp > output/x-artigos-2.links
import scrapy

import json
import requests
import logging

from bs4 import BeautifulSoup
from lxml import html
from pymongo import MongoClient
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class DBLP_Spider(scrapy.Spider):
    name = "dblp"

    start_urls = []
    filepath = 'output/links/x-venues-2.links'
    with open(filepath, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]

    # ======= Links =======

    def extract_doi_links(self, response):
        xpath_string = "//li/a[not(@class) and contains(@href, 'https://doi.org/')]/@href"
        links = response.xpath(xpath_string).getall()

        if (links == []):
            xpath_string = "//li/a[contains(@href, '//dl.acm.org/')]/@href"
            links = response.xpath(xpath_string).getall()

        return links

    ##############################################

    def remove_tags(self, string):
        return BeautifulSoup(string, "lxml").text
    
    ##############################################

    def parse(self, response):
        links = self.extract_doi_links(response)
        # print(response.request.url)
        for l in links:
            print(l)