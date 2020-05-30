# python3 simplify_data.py
import pymongo

from bson.objectid import ObjectId
from utils import dict_print, pprint, sanitize, stats

def setup():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db_from = client["venues"]
    db_to   = client["venues_simple"]
    
    return db_from, db_to

#####################################

def find_author(collection, object_id):
    return collection.find_one({ '_id' : object_id }, {'_id': False})

#####################################

def get_authors(db, col_name, article_id):
    authors = []
    authors_ids = []


    # print("\nAuthors (Done) ")
    for ref in db[col_name + '_authors_articles'].find({ 'article_id' : article_id }, {'_id' : False}):
        if (ref in authors_ids): continue
        authors_ids.append(ref)

        this_author = find_author(db[col_name + '_authors'], ref['author_id'])
        d = {}
        d['name'] = this_author['name']
        d['institute'] = this_author['institute']

        authors.append(d)

    return authors


def get_venue(db_from, col_name, publication_id):
    venue = db_from[col_name + '_publications'].find_one({ '_id' : publication_id }, {'_id' : False})
    return venue

def get_data(db_from, db_to, col_name, start):
    col_get  = db_from[col_name + '_articles']
    col_post = db_to[col_name]
    col_art  = db_to['articles']

    count = start

    for article in col_get.find({}, no_cursor_timeout=True)[start:]:
        repeat = True
        while(repeat):
            try:
                if (article['title'] == ''): 
                    repeat = False
                    continue

                authors = get_authors (db_from, col_name, article['_id'])
                venue   = get_venue   (db_from, col_name, article['publication_id'])

                article.pop('_id', None)
                article.pop('publication_id', None)
                
                article['authors'] = authors
                article['venue'] = venue

                # if (count % 10 == 0):
                col_post.insert_one(article)
                col_art.insert_one(article)
                print('(', count, '/ 51703 )')
                count += 1
                repeat = False
            
            except CursorNotFound:
                print('Deu erro, tentando novamente...')
                repeat = True


def main():
    db_from, db_to = setup()
    col_name = 'acm'

    # stats(db)
    start = 23
    # for i in range(start, end, 1):
        # print('Progress:', i, '/', end)
    get_data(db_from, db_to, col_name, start)



if __name__ == "__main__": main()