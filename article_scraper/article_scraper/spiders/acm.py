# scrapy crawl acm > tests/0-interaction/data/dl-acm-org.data
# scrapy crawl acm > data/acm/10-acm.data
import scrapy

import json
import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient


class ACM_Spider(scrapy.Spider):
    name = "acm"

    # filepath = 'tests/0-interaction/links/dl-acm-org.links'
    filepath = 'input/10-acm.links'
    with open(filepath, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]

    ##############################################

    # ======= Articles =======

    def extract_abstract(self, response):
        xpath_string = "//div[@class='article__section article__abstract hlFld-Abstract']/p/descendant::text()"
        abstract = response.xpath(xpath_string).getall()

        if( len(abstract) == 0):
            xpath_string = "//div[@class='abstractSection abstractInFull']/p/descendant::text()"
            abstract = response.xpath(xpath_string).getall()

        if( len(abstract) > 0 ):
            abstract = ''.join(abstract)
            return str(abstract)
        
        return ""

    def extract_date(self, response):
        date = ""
        for dates_raw in response.xpath("//span[@class='epub-section__date']"):
            date_scraped = dates_raw.xpath("./text()").extract_first()
            date = date_scraped.strip()

        return str(date)

    def extract_doi(self, response):
        xpath_string = "//input[@name='doiVal']/@value"
        doi = response.xpath(xpath_string).get()

    def extract_journal(self, response):
        return ''
    
    def extract_keywords(self, response):
        return []
    
    def extract_link(self, response):
        return response.request.url

    def extract_pages(self, response):
        pages = ""
        for pages_raw in response.xpath("//span[@class='epub-section__pagerange']"):
            pages_scraped = pages_raw.xpath("./text()").extract_first()
            pages = pages_scraped.strip()

        if( pages != ""):
            pages = pages.replace('Pages', '')
            pages = pages.replace(' ', '')
            dash = ""
            for ch in pages:
                if(not ch.isdigit()):
                    dash = ch

            if(dash != ""):
                pages = pages.split(dash)
                pages = int(pages[1]) - int(pages[0]) + 1
        
        if pages == "":
            pages = 0

        return str(pages)

    def extract_references(self, response):
        references = []
        for references_raw in response.xpath("//span[@class='references__note']"):
            current_reference = ""
            nodes = references_raw.xpath("./descendant::text()").getall()
            for n in nodes[0:-1]:
                current_reference += n
            
            if( current_reference not in references):
                references.append(current_reference )

        return references

    def extract_title(self, response):
        xpath_string = "//h1[@class='citation__title']/text()"
        title = response.xpath(xpath_string).getall()
        title = ''.join(title)

        return str(title)

        return str(doi)

    # ======= Authors =======

    def extract_authors(self, response):
        authors = []
        authors_names = []
        for author_names_raw in response.xpath("//a[@class='author-name']"):
            name = author_names_raw.xpath("./@title").extract_first()

            institute = author_names_raw.xpath("./span/span[@class='loa_author_inst']/p/text()").extract_first()
            if(institute is None):
                institute = ""


            if(name not in authors_names):
                new_author = dict()
                new_author['name'] = name
                new_author['institute']  = institute
                authors.append(new_author)

                authors_names.append(name)
        
        return authors

    # ======= Publications =======

    def extract_publication(self, response):
        xpath_string = "//div[@class='issue-item__detail']/a/@href"
        url = response.xpath(xpath_string).get()
        url = response.urljoin(url)

        publication = dict()
        new_response = requests.get(url)
        code = new_response.text.split('\n')

        title = ""
        publisher = ""
        conference = ""
        code = list( filter(lambda a: a != '', code) )
        
        for i in range(len(code)):
            if( "Publisher:" in code[i]):
                publisher = code[i].split('<ul class="rlist--inline comma">')[1]
                publisher = publisher.split('</ul>')[0]
                publisher = self.remove_tags(publisher)
                publisher = publisher.replace("Publisher:", "")


                conference = ""
                conference = self.remove_tags( code[i] )
                conference = conference.replace("Publisher:", "")
                aux = conference.split("Conference:")

                if(len(aux) == 1):
                    conference = ""

                if(len(aux) > 1):
                    conference = self.remove_tags( aux[1] )
                    conference = conference.strip(' ')

                print( "Publisher  - " + publisher )
                print( "Conference - " + conference )

            if( "<title>" in code[i] ):
                title = self.remove_tags( code[i] )
                title = title.split( ' | ' )[0]

        publication['title'] = title
        publication['publisher'] = publisher
        publication['conference'] = conference
        publication['url'] = url

        return publication

    ##############################################

    def remove_tags(self, string):
        return BeautifulSoup(string, "lxml").text
    
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

    def save_publication(self, database, publication):
        client = MongoClient()
        db = client[database]
        collection = db['acm-publications']

        result = collection.find_one(publication)
        if (result == None):
            publication_id = collection.insert_one(publication).inserted_id
            return publication_id
        else:
            return result['_id']

    def save_article(self, database, article, publication):
        client = MongoClient()
        db = client[database]
        collection = db['acm-articles']

        publication_id = self.get_publication_id(database, publication)
        if (publication_id != ""):
            article['publication_id'] = publication_id

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

    def save(self, database, authors, article, publication):
        self.save_authors(database, authors)
        self.save_publication(database, publication)
        self.save_article(database, article, publication)

        self.save_authors_articles(database, authors, article)

    def get_publication_id(self, database, publication):
        client = MongoClient()
        db = client[database]
        collection = db['acm-publications']

        result = collection.find_one(publication)
        if(result == None):
            return ""

        return result['_id']
    
    ##############################################

    def parse(self, response):

        authors = []
        article = {}
        publication = {}

        article['abstract']     = self.extract_abstract(response)
        article['date']         = self.extract_date(response)
        article['doi']          = self.extract_doi(response)
        article['journal']      = self.extract_journal(response)  # Returns ''
        article['keywords']     = self.extract_keywords(response) # Returns []
        article['link']         = self.extract_link(response)
        article['pages']        = self.extract_pages(response)
        article['references']   = self.extract_references(response)
        article['title']        = self.extract_title(response)

        authors = self.extract_authors(response)
        publication  = self.extract_publication(response) # FIX THIS

        self.debug_print(authors, article, publication)

        database = 'interaction'
        # self.save(database, authors, article, publication)
