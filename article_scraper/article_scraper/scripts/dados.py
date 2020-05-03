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

def insert_journal(db, col_name, publication_id):
        print("\nJournal: ")
        pprint( db[col_name + '_publications'].find_one({ '_id' : publication_id }, {'_id' : False}) )

def insert_references(db, col_name, references):
        print('\nReferences')
        for ref in references:
            print('\t->', ref)

def insert_keywords(db, col_name, keywords):
        print('\nKeywords')
        for kw in keywords:
            print('\t->', kw)

def insert_articles(db, col_name):
    collection = db[col_name + '_articles']

    for article in collection.find({}):
        if (article['title'] == ''): continue
        pprint(article)

        insert_keywords(db, col_name, article['keywords'])
        insert_references(db, col_name, article['references'])

        authors = []
        print("\nAuthors: ")
        for ref in db[col_name + '_authors_articles'].find({ 'article_id' : article['_id'] }, {'_id' : False}):
            if (ref in authors): continue
            authors.append(ref)

            author_id = ref['author_id']
            pprint(find_author(db[col_name + '_authors'], author_id))

        insert_journal(db, col_name, article['publication_id'])

        return


def main():
    db = setup()
    # stats(db)

    insert_articles(db, 'acm')



if __name__ == "__main__": main()