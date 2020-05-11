# python3 dados.py
import pymongo

from bson.objectid import ObjectId
from utils import dict_print, pprint, stats


def setup():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["venues"]
    
    return db

#####################################

def find_author(collection, object_id):
    return collection.find_one({ '_id' : object_id }, {'_id': False})

#####################################

def acm_authors(db):
    collection = db['acm_authors']
    pprint(find_author(collection, ObjectId('5e90cd4b8a0d9f37a6a96bc3')))

def insert_articles(db, col_name, article):
    print("\nArticle: ")

    print('\t\'abstract\':', article['abstract'])
    print('\t\'date\':',     article['date'])
    print('\t\'doi\':',      article['doi'])
    print('\t\'journal\':',  article['journal'])
    print('\t\'link\':',     article['link'])
    print('\t\'pages\':',    article['pages'])
    print('\t\'title\':',    article['title'])


def insert_authors(db, col_name, article_id):
    authors = []
    authors_ids = []

    print("\nAuthors: ")
    for ref in db[col_name + '_authors_articles'].find({ 'article_id' : article_id }, {'_id' : False}):
        if (ref in authors_ids): continue
        authors_ids.append(ref)

        this_author = find_author(db[col_name + '_authors'], ref['author_id'])
        if (type(this_author['institute']) == list):
            this_author['institute'] = ", ".join(this_author['institute'])
        authors.append(this_author)

    pprint(authors)

def insert_venue(db, col_name, publication_id):
        print("\nVenue: ")
        pprint( db[col_name + '_publications'].find_one({ '_id' : publication_id }, {'_id' : False}) )

def insert_references(db, col_name, references):
        print('\nReferences')
        for ref in references:
            print('\t->', ref)

def insert_keywords(db, col_name, keywords):
        print('\nKeywords')
        for kw in keywords:
            print('\t->', kw)

def get_data(db, col_name):
    collection = db[col_name + '_articles']

    count = 0

    for article in collection.find({}):
        if (article['title'] == ''): continue
        pprint(article)

        insert_venue      (db, col_name, article['publication_id'])
        insert_articles   (db, col_name, article)
        insert_authors    (db, col_name, article['_id'])
        insert_keywords   (db, col_name, article['keywords'])
        insert_references (db, col_name, article['references'])

        print('\n======================')
        
        count += 1
        if (count == 3):
            return


def main():
    db = setup()
    # stats(db)

    col_name = 'acm'

    get_data(db, col_name)



if __name__ == "__main__": main()