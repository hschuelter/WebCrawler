# scrapy crawl springer_chapters > tests/0-interaction/data/link-springer-com.data
# scrapy crawl springer_chapters > data/springer/10-springer-chapters.data
import scrapy
import requests
import unicodedata

from bs4 import BeautifulSoup
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess

class ACM_Chapter_Spider(scrapy.Spider):
    name = "springer_chapters"
    
    filepath = 'input/10-springer.links'
    # filepath = 'tests/0-interaction/data/link-springer-com.data'
    with open(filepath, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]
    start_urls = list(filter (lambda u: 'link.springer.com/chapter/' in u, start_urls))

    ##############################################

    # ======= Articles =======

    def extract_abstract(self, response):
        xpath_string = "//p[@class='Para']/text()"
        abstract = response.xpath(xpath_string).getall()
        abstract = ''.join(abstract)
        
        return str(abstract)

    def extract_book(self, response):
        xpath_string = "//a[@class='gtm-book-series-link']/text()"
        book = response.xpath(xpath_string).getall()
        book = ''.join(book)

        return str(book)

    def extract_date(self, response):
        xpath_string = "//time/text()"
        date = response.xpath(xpath_string).getall()
        date = ''.join(date)

        return str(date)

    def extract_doi(self, response):
        xpath_string = "//span[@id='doi-url']/text()"
        doi = response.xpath(xpath_string).get()

        return str(doi)

    def extract_journal(self, response):
        return ''

    def extract_keywords(self, response):
        keywords = []
        for keyword_raw in response.xpath("//span[@class='Keyword']").getall():
            current_keyword = self.remove_tags(keyword_raw)
            current_keyword = unicodedata.normalize("NFKD", current_keyword)
            keywords.append(current_keyword)

        return keywords

    def extract_link(self, response):
        return response.request.url

    def extract_pages(self, response):
        xpath_string = '//span[@class="page-numbers-info"]/text()'
        pages = response.xpath(xpath_string).getall()
        pages = ''.join(pages)
        pages = pages.replace('pp ', '')

        start, end = map(lambda x : int(x), pages.split('-'))

        return str(end-start)

    def extract_publisher(self, response):
        xpath_string = "//span[@id='publisher-name']/text()"
        publisher = response.xpath(xpath_string).getall()
        publisher = ''.join(publisher)

        return str(publisher)

    def extract_references(self, response):
        references = []
        for references_raw in response.xpath("//li[@class='Citation']").getall():
            current_reference = self.remove_tags(references_raw)
            references.append(current_reference)

        return references

    def extract_title(self, response):
        xpath_string = "//h1[@class='ChapterTitle']/text()"
        title = response.xpath(xpath_string).getall()
        title = ''.join(title)

        return str(title)

    # ======= Authors =======

    def extract_authors(self, response): #***********************
        xpath_string = "//meta[@name='citation_author_institution' or @name='citation_author']"

        authors = []
        author_name = ''
        author_institute = ''

        _dict_ = {}
        for a in response.xpath(xpath_string):
            label = a.xpath("./@name").get()
            if(label == 'citation_author'):
                if bool(_dict_):
                    authors.append(_dict_)
                
                _dict_ = {}
                author_name = a.xpath("./@content").get()
                _dict_['name'] = author_name
                _dict_['institute'] = []
                continue
        
            if(label == 'citation_author_institution'):
                author_institute = a.xpath("./@content").get()
                if(not author_institute in _dict_['institute']):
                    _dict_['institute'].append(author_institute)
                continue
            
        if bool(_dict_):
            authors.append(_dict_)

        return authors

    # ======= Publications =======

    def extract_publication(self, response):
        return {}
    # # Posso utilizar no futuro
    # def extract_conference(self, response): #***********************
    #     conference = ""
    #     for conference_raw in response.xpath("//span[@class='epub-section__title']"):
    #         conference_scraped = conference_raw.xpath("./text()").extract_first()
    #         conference = conference_scraped.strip()

    #     return str(conference)

    ##############################################

    def remove_tags(self, string):
        return BeautifulSoup(string, "lxml").text
    
    ##############################################

    def debug_print(self, authors, article):
        print('Link:', article['link'])
        print("\nAuthors: ")
        for a in authors:
            print('\t' + str(a))
        print("\nTitle:", article['title'])
        print("\nAbstract:", article['abstract'])
        print("Date:", article['date'])
        print("Pages:", article['pages'])
        print("DOI:", article['doi'])
        print("Publisher:", article['publisher'])
        print("Book:", article['book'])
        print("Journal:", article['journal'])
        print("Keywords:", article['keywords'])
        print("\nReferences: ")
        for ref in article['references']:
            print('\t' + ref)
        print("=========================")

    ############################################## 
    
    def save_authors(self, database, authors):
        client = MongoClient()
        db = client[database]
        collection = db['springer-authors']

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
        collection = db['springer-publications']

        result = collection.find_one(publication)
        if (result == None):
            publication_id = collection.insert_one(publication).inserted_id
            return publication_id
        else:
            return result['_id']

    def save_article(self, database, article):
        client = MongoClient()
        db = client[database]
        collection = db['springer-articles']

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
        
        authors_collection = db['springer-authors']
        article_collection = db['springer-articles']

        collection = db['springer-authors-articles']

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
        collection = db['springer-publications']

        result = collection.find_one(publication)
        if(result == None):
            return ""

        return result['_id']
    
    ##############################################

    def parse(self, response):

        article = {}
        authors = []
        publication = {}

        article['abstract']   = self.extract_abstract(response)
        article['book']       = self.extract_book(response)
        article['date']       = self.extract_date(response)
        article['doi']        = self.extract_doi(response)
        article['journal']    = self.extract_journal(response) # Returns ''
        article['keywords']   = self.extract_keywords(response)
        article['link']       = self.extract_link(response)
        article['pages']      = self.extract_pages(response)
        article['publisher']  = self.extract_publisher(response)
        article['references'] = self.extract_references(response)
        article['title']      = self.extract_title(response)
        

        authors = self.extract_authors(response)
        publication = self.extract_publication(response)
        
        self.debug_print(authors, article)

        database = 'interaction'
        # self.save(database, authors, article, publication)

        