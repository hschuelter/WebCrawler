# scrapy crawl ieeex > output/ban/ieeex.data
import scrapy

import html
import json
import logging

from bs4 import BeautifulSoup
# from pymongo import MongoClient


class IEEEX_Spider(scrapy.Spider):
    name = "ieeex"
    
    filepath = './input/ban/10-ieeex.links'
    with open(filepath, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]

    ##############################################

    def extract_metadata(self, response):
        metadata = []
        for raw_text in response.xpath("//script[@type='text/javascript']"):
            helper = raw_text.xpath("./text()").extract_first()
            if ((helper is not None) and ("global.document.metadata" in helper)):
                metadata = helper.split('\n')
                break

        for m in metadata:
            if ('global.document.metadata' in m):
                idx = m.find('{')
                m = m[idx:]
                meta = self.to_dict(m)

                return meta
        
        return ''

    ##############################################

    # ======= Articles =======

    def extract_abstract(self, metadata):
        key = 'abstract'
        
        if key not in metadata:
            return ""   

        abstract = metadata[key]
        abstract = abstract
        abstract = self.remove_tags(abstract)
        abstract = html.unescape(abstract)
        return abstract

    def extract_date(self, metadata):
        key = 'chronOrPublicationDate'

        if key not in metadata:
            return ""   

        date = metadata[key]
        date = self.remove_tags(date)
        date = html.unescape(date)
        return date

    def extract_doi(self, metadata):
        key = 'doi'

        if key not in metadata:
            return ""  

        doi = metadata[key]
        return doi

    def extract_journal(self, metadata):
        key = 'displayPublicationTitle'

        if key not in metadata:
            return ""   
            
        journal = metadata[key]
        journal = self.remove_tags(journal)
        journal = html.unescape(journal)
        return journal

    def extract_keywords(self, metadata):
        key = 'keywords'

        if key not in metadata:
            return []        

        array = metadata[key]

        keywords = []
        for a in array:
            for kw in a['kwd']:
                k = html.unescape(kw) 
                keywords.append( k )

        return keywords

    def extract_link(self, response):
        return response.request.url

    def extract_pages(self, metadata):
        key_start = 'startPage'
        key_end   = 'endPage'

        if ( (key_start not in metadata) or (key_end not in metadata)):
            return "0"

        start_page = metadata[key_start]
        end_page = metadata[key_end]

        try:
            pages = int(end_page) - int(start_page)
        except ValueError:
            pages = start_page + ' - ' + end_page
            pass

        return str(pages)

    def extract_references(self, metadata):
        return []

    def extract_title(self, metadata):
        key = 'title'
        
        if key not in metadata:
            return ""  

        title = metadata[key]
        title = self.remove_tags(title)
        title = html.unescape(title)
        return title  

    # ======= Authors =======

    def extract_authors(self, metadata):
        key = 'authors'

        if key not in metadata:
            return []        

        authors = []
        raw_data = metadata[key]
        
        for r in raw_data:
            author_info = dict()

            author = r['name']
            author = self.remove_tags(author)
            author = html.unescape(author)
            author_info['name'] = author

            institute = r['affiliation']
            institute = self.remove_tags(institute)
            institute = html.unescape(institute)
            author_info['institute'] = institute

            authors.append( author_info )

        return authors

    # ======= Publications =======

    def extract_publication(self, metadata):
        publication = {}
        
        publication['publisher'] = self.extract_publication_publisher(metadata)
        publication['title']     = self.extract_publication_title(metadata)
        publication['date']      = self.extract_date(metadata)
        publication['url']       = self.extract_publication_link(metadata)

        return publication

    def extract_publication_publisher(self, metadata):
        key = 'publisher'

        if key not in metadata:
            return ""   

        publisher = metadata[key]
        publisher = self.remove_tags(publisher)
        publisher = html.unescape(publisher)
        return publisher

    def extract_publication_title(self, metadata):
        key = 'publicationTitle'

        if key not in metadata:
            return ""   

        publication_title = metadata[key]
        publication_title = self.remove_tags(publication_title)
        publication_title = html.unescape(publication_title)

        return publication_title

    def extract_publication_link(self, metadata):
        key = 'pubLink'

        if key not in metadata:
            return ""   

        publication_link = 'https://ieeexplore.ieee.org' + metadata[key]

        return publication_link

    ##############################################
    
    def remove_tags(self, string):
        return BeautifulSoup(string, "lxml").text

    def to_dict(self, raw_metadata):
        raw_metadata = raw_metadata.strip(';')
        return json.loads(raw_metadata)

    ############################################## 

    def print_metadata(self, metadata):
        for key, value in metadata.items():
            print(key, '->', value)

    def debug_print(self, authors, article, publication):
        print('Link:', article['link'])
        print("Authors: ")
        for a in authors:
            print( '\t' + a['name'] + ' (' + a['institute'] + ')' )
        print("\nTitle:", article['title'])
        print("\nAbstract:", article['abstract'])
        print("Journal:", article['journal'])
        print("Date:", article['date'])
        print("Pages:", article['pages'])
        print("DOI:", article['doi'])
        print("Publication:", publication)
        print("Keywords:", article['keywords'])
        print("References:", article['references'])

        print("\n=========================")

    ############################################## 
    
    def save_authors(self, database, authors):
        client = MongoClient()
        db = client[database]
        collection = db['ieeex_authors']

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

    def save_publication(self, database, publication):
        client = MongoClient()
        db = client[database]
        collection = db['ieeex_publications']

        result = collection.find_one(publication)
        if (result == None):
            publication_id = collection.insert_one(publication).inserted_id
            return publication_id
        else:
            return result['_id']

    def save_article(self, database, article, publication):
        client = MongoClient()
        db = client[database]
        collection = db['ieeex_articles']

        publication_id = self.get_publication_id(database, publication)
        if (publication_id != ""):
            article['publication_id'] = publication_id

        result = collection.find_one(article)
        if (result == None):
            article_id = collection.insert_one(article).inserted_id
            return article_id
        else:
            return result['_id']

    def save_authors_articles(self, database, authors, article):
        client = MongoClient()
        db = client[database]
        
        authors_collection = db['ieeex_authors']
        article_collection = db['ieeex_articles']

        collection = db['ieeex_authors_articles']

        article_id = article_collection.find_one(article)['_id']
        for a in authors:
            author_id = authors_collection.find_one(a)['_id']

            post = {}
            post['author_id']  = author_id
            post['article_id'] = article_id
            collection.insert_one(post)

    def save(self, database, authors, article, publication):
        self.save_authors(database, authors)
        self.save_publication(database, publication)
        self.save_article(database, article, publication)

        self.save_authors_articles(database, authors, article)

    def get_publication_id(self, database, publication):
        client = MongoClient()
        db = client[database]
        collection = db['ieeex_publications']

        result = collection.find_one(publication)
        if(result == None):
            return ""

        return result['_id']
    
    ##############################################

    def parse(self, response):

        metadata = self.extract_metadata(response)
        if (metadata == ''):
            return

        article = {}
        authors = []
        publication = {}

        article['abstract']   = self.extract_abstract(metadata)
        article['date']       = self.extract_date(metadata)
        article['doi']        = self.extract_doi(metadata)
        article['journal']    = self.extract_journal(metadata)
        article['keywords']   = self.extract_keywords(metadata)
        article['link']       = self.extract_link(response)
        article['pages']      = self.extract_pages(metadata)
        article['references'] = self.extract_references(metadata) # Returns [] 
        article['title']      = self.extract_title(metadata)
        
        authors     = self.extract_authors(metadata)
        publication = self.extract_publication(metadata)
        
        self.debug_print(authors, article, publication)
        
        # database = 'venues'
        # self.save(database, authors, article, publication)