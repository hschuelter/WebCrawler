# scrapy crawl ieeex -o Data/x.json > Data/ieee.data
# scrapy crawl ieeex > data/ieeex/10-ieeex.data
import scrapy

import html
import json

from bs4 import BeautifulSoup
from pymongo import MongoClient


class IEEEX_Spider(scrapy.Spider):
    name = "ieeex"
    
    with open("input/10-ieeex.links", "r") as f:
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
            
    def extract_title(self, metadata):
        key = 'title'
        
        if key not in metadata:
            return ""    


        title = metadata[key]
        title = self.remove_tags(title)
        title = html.unescape(title)
        return title

    def extract_abstract(self, metadata):
        key = 'abstract'
        
        if key not in metadata:
            return ""   

        abstract = metadata[key]
        abstract = abstract
        abstract = self.remove_tags(abstract)
        abstract = html.unescape(abstract)
        return abstract

    def extract_journal(self, metadata):
        key = 'displayPublicationTitle'

        if key not in metadata:
            return ""   
            
        journal = metadata[key]
        journal = self.remove_tags(journal)
        journal = html.unescape(journal)
        return journal

    def extract_date(self, metadata):
        key = 'chronOrPublicationDate'

        if key not in metadata:
            return ""   

        date = metadata[key]
        date = self.remove_tags(date)
        date = html.unescape(date)
        return date

    def extract_num_pages(self, metadata):
        key_start = 'startPage'
        key_end   = 'endPage'

        if ( (key_start not in metadata) or (key_end not in metadata)):
            return "0"

        start_page = metadata[key_start]
        end_page = metadata[key_end]

        try:
            num_pages = int(end_page) - int(start_page)
        except ValueError:
            num_pages = start_page + ' - ' + end_page
            pass

        return str(num_pages)

    def extract_doi(self, metadata):
        key = 'doi'

        if key not in metadata:
            return ""  

        doi = metadata[key]
        return doi

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

    def extract_publisher(self, metadata):
        key = 'publisher'

        if key not in metadata:
            return ""   

        publisher = metadata[key]
        publisher = self.remove_tags(publisher)
        publisher = html.unescape(publisher)
        return publisher

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

    def debug_print(self, authors, article):
        print('Link:', article['link'])
        print("Authors: ")
        for a in authors:
            print( '\t' + a['name'] + '( ' + a['institute'] + ' )' )
        print("\nTitle: \"" + article['title'] + "\"")
        print("\nAbstract: \"" + article['abstract'] + "\"")
        print("Journal: \"" + article['journal'] + "\"")
        print("Date: \"" + article['date'] + "\"")
        print("Pages: \"" + article['num_pages'] + "\"")
        print("DOI: \"" + article['doi'] + "\"")
        print("Publisher: \"" + article['publisher'] + "\"")
        print("Keywords: ", end="")
        print( article['keywords'] )

        print("\n=========================")

    ############################################## 
    
    def save_authors(self, authors):
        client = MongoClient()
        db = client['ieeex']
        collection = db['ieeex-authors']

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
        db = client['ieeex']
        collection = db['ieeex-articles']

        result = collection.find_one(article)
        if (result == None):
            article_id = collection.insert_one(article).inserted_id
            return article_id
        else:
            return result['_id']

    def save_authors_articles(self, authors, article):
        client = MongoClient()
        db = client['ieeex']
        
        authors_collection = db['ieeex-authors']
        article_collection = db['ieeex-articles']

        collection = db['ieeex-authors-articles']

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
        # o title
        # o authors
        # o abstract
        # o conference/journal
        # o date
        # o pages
        # o doi
        # x citations
        # x references

        metadata = self.extract_metadata(response)
        if (metadata == ''):
            return

        article = {}
        article['title']     = self.extract_title(metadata)
        article['abstract']  = self.extract_abstract(metadata)
        article['journal']   = self.extract_journal(metadata)
        article['date']      = self.extract_date(metadata)
        article['num_pages'] = self.extract_num_pages(metadata)
        article['doi']       = self.extract_doi(metadata)
        article['keywords']  = self.extract_keywords(metadata)
        article['publisher'] = self.extract_publisher(metadata)
        article['link']      = response.request.url
        
        authors = self.extract_authors(metadata)
        
        self.debug_print(authors, article)

        self.save(authors, article)