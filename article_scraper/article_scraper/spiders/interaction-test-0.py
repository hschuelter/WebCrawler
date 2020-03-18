# scrapy crawl interaction > tests/0-interaction/interaction-conference.data
import scrapy

import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient


class Interaction_Spider(scrapy.Spider):
    name = "interaction"

    filename = 'tests/0-interaction/interaction-conference.links'
    with open(filename, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]


    def extract_title(self, response):
        xpath_string = "//h1"
        title = response.xpath(xpath_string).getall()
        title = ''.join(title).replace('\n', '')
        title = self.remove_tags(title)

        return str(title)

    def extract_articles(self, response):
        xpath_string = "//a/@href"
        articles = response.xpath(xpath_string).getall()
        articles = list(filter(lambda link: 'https://doi.org/' in link, articles))

        return articles

    ##############################################

    def remove_tags(self, string):
        return BeautifulSoup(string, "lxml").text
    
    ##############################################
    
    def debug_print(self, conference):
        print('Title:', conference['title'])
        print('Articles:', conference['articles'])
        print('Number of articles:', conference['num'])
        print('Link:', conference['link'])
        print("\n=========================")

    def link_print(self, articles):
        fp = open('tests/0-interaction/artigos.links', 'a')

        for a in articles:
            print(a, file=fp)

        fp.close()

    ##############################################
    
    def save_authors(self, authors):
        client = MongoClient()
        db = client['acm']
        collection = db['acm-authors']

        id_array = []
        for a in authors:
            result = collection.find_one(a)
            if (result == None):
                author_id = collection.insert_one(a).inserted_id
                id_array.append(author_id)
            else:
                author_id = result['_id']
                id_array.append(author_id)
        
        return id_array

    def save_article(self, article):
        client = MongoClient()
        db = client['acm']
        collection = db['acm-articles']

        result = collection.find_one(article)
        if (result == None):
            article_id = collection.insert_one(article).inserted_id
            return article_id
        else:
            return result['_id']

    def save_authors_articles(self, authors, article):
        client = MongoClient()
        db = client['acm']
        
        authors_collection = db['acm-authors']
        article_collection = db['acm-articles']

        collection = db['acm-authors-articles']

        article_id = article_collection.find_one(article)['_id']
        for a in authors:
            author_id = authors_collection.find_one(a)['_id']

            post = {}
            post['author_id']  = author_id
            post['article_id'] = article_id
            collection.insert_one(post)

    def save(self, authors, article):
        au  = self.save_authors(authors)
        art = self.save_article(article)

        print(au, art)
        self.save_authors_articles(authors, article)
    
    ##############################################

    def parse(self, response):
        conference = {}

        conference['title']     = self.extract_title(response)
        conference['articles']  = self.extract_articles(response)
        conference['num']       = len(conference['articles'])
        conference['link']      = response.request.url

        # self.debug_print(conference)
        # self.link_print(conference['articles'])
