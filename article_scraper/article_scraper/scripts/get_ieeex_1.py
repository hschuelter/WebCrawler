# python3 get_ieeex_1.py > tests/1-venues/data/ihc/ieeexplore-ieee-org-1.data
import json
import logging, sys
import re
import requests
import time
import html as ht

from bs4 import BeautifulSoup
from pymongo import MongoClient

from functools import reduce
from lxml import html

def log(message):
    logging.debug(message)
    time.sleep(0.1)

def extract_metadata(url):
    sucess = False
    while not sucess:
        try:
            r = requests.get(url)
            sucess = True
        except:
            log('Error, trying again in 1 second')
            time.sleep(1.0)
    r.encoding = r.apparent_encoding
    con = r.text.split('\n')
    con = list(map(lambda x : x.replace('\t', ''), con))
    con = list(filter(lambda x : 'global.document.metadata' in x, con))
    for c in con:
        idx = c.find('{')
        metadata = c[idx:-1]
        return json.loads(metadata)

    return ''

    ##############################################

    # ======= Articles =======

def extract_abstract(metadata):
    key = 'abstract'
    
    if key not in metadata:
        return ""   

    abstract = metadata[key]
    abstract = abstract
    abstract = remove_tags(abstract)
    abstract = ht.unescape(abstract)
    return abstract

def extract_date(metadata):
    key = 'chronOrPublicationDate'

    if key not in metadata:
        return ""   

    date = metadata[key]
    date = remove_tags(date)
    date = ht.unescape(date)
    return date

def extract_doi(metadata):
    key = 'doi'

    if key not in metadata:
        return ""  

    doi = metadata[key]
    return doi

def extract_journal(metadata):
    key = 'displayPublicationTitle'

    if key not in metadata:
        return ""   
        
    journal = metadata[key]
    journal = remove_tags(journal)
    journal = ht.unescape(journal)
    return journal

def extract_keywords(metadata):
    key = 'keywords'

    if key not in metadata:
        return []        

    array = metadata[key]

    keywords = []
    for a in array:
        for kw in a['kwd']:
            k = ht.unescape(kw) 
            keywords.append( k )

    return keywords

def extract_link(url):
    return url

def extract_pages(metadata):
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

def extract_references(metadata):
    return []

def extract_title(metadata):
    key = 'title'
    
    if key not in metadata:
        return ""  

    title = metadata[key]
    title = remove_tags(title)
    title = ht.unescape(title)
    return title  

# ======= Authors =======

def extract_authors(metadata):
    key = 'authors'

    if key not in metadata:
        return []        

    authors = []
    raw_data = metadata[key]
    
    for r in raw_data:
        author_info = dict()

        author = r['name']
        author = remove_tags(author)
        author = ht.unescape(author)
        author_info['name'] = author

        institute = r['affiliation']
        institute = remove_tags(institute)
        institute = ht.unescape(institute)
        author_info['institute'] = institute

        authors.append( author_info )

    return authors

# ======= Publications =======

def extract_publication(metadata):
    publication = {}
    
    publication['publisher'] = extract_publication_publisher(metadata)
    publication['title']     = extract_publication_title(metadata)
    publication['date']      = extract_date(metadata)
    publication['url']       = extract_publication_link(metadata)

    return publication

def extract_publication_publisher(metadata):
    key = 'publisher'

    if key not in metadata:
        return ""   

    publisher = metadata[key]
    publisher = remove_tags(publisher)
    publisher = ht.unescape(publisher)
    return publisher

def extract_publication_title(metadata):
    key = 'publicationTitle'

    if key not in metadata:
        return ""   

    publication_title = metadata[key]
    publication_title = remove_tags(publication_title)
    publication_title = ht.unescape(publication_title)

    return publication_title

def extract_publication_link(metadata):
    key = 'pubLink'

    if key not in metadata:
        return ""   

    publication_link = 'https://ieeexplore.ieee.org' + metadata[key]

    return publication_link

##############################################

def remove_tags(string):
    return BeautifulSoup(string, "lxml").text

def to_dict(raw_metadata):
    raw_metadata = raw_metadata.strip(';')
    return json.loads(raw_metadata)

############################################## 

def print_metadata(metadata):
    for key, value in metadata.items():
        print(key, '->', value)

def debug_print(authors, article, publication):
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

def save_authors(database, authors):
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

def save_publication(database, publication):
    client = MongoClient()
    db = client[database]
    collection = db['ieeex_publications']

    result = collection.find_one(publication)
    if (result == None):
        publication_id = collection.insert_one(publication).inserted_id
        return publication_id
    else:
        return result['_id']

def save_article(database, article, publication):
    client = MongoClient()
    db = client[database]
    collection = db['ieeex_articles']

    publication_id = get_publication_id(database, publication)
    if (publication_id != ""):
        article['publication_id'] = publication_id

    result = collection.find_one(article)
    if (result == None):
        article_id = collection.insert_one(article).inserted_id
        return article_id
    else:
        return result['_id']

def save_authors_articles(database, authors, article):
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

def save(database, authors, article, publication):
    save_authors(database, authors)
    save_publication(database, publication)
    save_article(database, article, publication)

    save_authors_articles(database, authors, article)
    log('Salvo no MongoDB')

def get_publication_id(database, publication):
    client = MongoClient()
    db = client[database]
    collection = db['ieeex_publications']

    result = collection.find_one(publication)
    if(result == None):
        return ""

    return result['_id']

##############################################

def parse(metadata, url):
    article = {}
    authors = []
    publication = {}

    article['abstract']   = extract_abstract(metadata)
    article['date']       = extract_date(metadata)
    article['doi']        = extract_doi(metadata)
    article['journal']    = extract_journal(metadata)
    article['keywords']   = extract_keywords(metadata)
    article['link']       = extract_link(url)
    article['pages']      = extract_pages(metadata)
    article['references'] = extract_references(metadata) # Returns [] 
    article['title']      = extract_title(metadata)
    
    authors     = extract_authors(metadata)
    publication = extract_publication(metadata)

    return authors, article, publication

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    filepath = 'tests/1-venues/IHC-links/ieeexplore-ieee-org-1.links'
    with open(filepath, "r") as f:
        start_urls = [url.strip() for url in f.readlines()]

    url_count = len(start_urls)
    count = 1

    for url in start_urls:
        log('========= Começando um artigo =========')
        log('Artigo: ' + str(count) + ' / ' + str(url_count))
        log('Url - ' + url)
        count += 1

        metadata = extract_metadata(url)
        if (metadata == '' or metadata == None):
            continue
        
        authors, article, publication = parse(metadata, url)
        debug_print(authors, article, publication)
        database = 'venues'
        save(database, authors, article, publication)

if __name__ == "__main__": main()