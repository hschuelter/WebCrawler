# python3 dados.py
import pymongo
from psycopg2 import connect, sql

from bson.objectid import ObjectId
from utils import dict_print, pprint, sanitize, stats

connection = connect (  user="arthur",
                        password="senha",
                        host="127.0.0.1",
                        port="5432",
                        database="venues_db")
cursor = connection.cursor()


def setup():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["venues"]
    
    return db

def insert_data(insert_query, input_):
    input_ = list(map(lambda x: sanitize(str(x)), input_))
    cursor.execute(insert_query, input_)
    connection.commit()
    
def retrieve_data(select_query, input_):
    input_ = list(map(lambda x: sanitize(str(x)), input_))
    cursor.execute(select_query, input_)
    data = cursor.fetchone()

    return data


#####################################

def find_author(collection, object_id):
    return collection.find_one({ '_id' : object_id }, {'_id': False})

#####################################

def insert_article(db, col_name, article, venue):
    # print("\nArticle: ")

    fk_venue = 0
    if (venue != None):
        fk_venue = venue[0]

    insert_query = """ INSERT INTO articles (title, abstract, pages, date, doi, link, tipo, fk_venue) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    select_query = """
        SELECT * 
        FROM articles 
        WHERE
            title = %s    AND
            abstract = %s AND
            pages = %s    AND
            date = %s     AND
            doi = %s      AND
            link = %s     AND
            tipo = %s     AND
            fk_venue = %s """

    
    article_input = [
        article['title'],   article['abstract'],    article['pages'],   article['date'],
        article['doi'],     article['link'],        "0",                fk_venue
    ]
    data = retrieve_data(select_query, article_input)
    
    if (data == None):
        print('\tPrecisa adicionar... ', end='')
        insert_data(insert_query, article_input)
        data = retrieve_data(select_query, article_input)

    # print(data)
    return data

def insert_authors(db, col_name, article_id):
    authors = []
    authors_ids = []

    insert_query = """ INSERT INTO authors (name, institute) VALUES (%s,%s)"""
    select_query = """ SELECT * FROM authors WHERE name = %s AND institute = %s """


    # print("\nAuthors (Done) ")
    for ref in db[col_name + '_authors_articles'].find({ 'article_id' : article_id }, {'_id' : False}):
        if (ref in authors_ids): continue
        authors_ids.append(ref)


        this_author = find_author(db[col_name + '_authors'], ref['author_id'])
        if (type(this_author['institute']) == list):
            this_author['institute'] = ", ".join(this_author['institute'])
        
        data = retrieve_data(select_query, [this_author['name'], this_author['institute']])

        if (data == None):
            # print("Precisa adicionar")
            insert_data(insert_query, [this_author['name'], this_author['institute']])
            data = retrieve_data(select_query, [this_author['name'], this_author['institute']])

        # pprint(data)
        this_author['id'] = data[0]
        authors.append(this_author)

    return authors

def insert_venue(db, col_name, publication_id):
    # print("\nVenue (Done)")
    venue = db[col_name + '_publications'].find_one({ '_id' : publication_id }, {'_id' : False})

    insert_query = """ INSERT INTO venues (title, publisher, link) VALUES (%s,%s,%s)"""
    select_query = """ SELECT * FROM venues WHERE title = %s AND publisher = %s AND link = %s"""

    data = retrieve_data(select_query, [venue['title'], venue['publisher'], venue['url']])
    
    if (data == None):
        # print('Precisa adicionar...')
        insert_data(insert_query, [venue['title'], venue['publisher'], venue['url']])
        data = retrieve_data(select_query, [venue['title'], venue['publisher'], venue['url']])

    # print(data)
    return data
    
def insert_citations(db, col_name, citations):
    # print('\nCitations')


    insert_query = """ INSERT INTO citations (citation) VALUES (%s)"""
    select_query = """ SELECT * FROM citations WHERE citation = %s"""

    citation_data = []

    for cit in citations:
        data = retrieve_data(select_query, [cit])
      
        if (data == None):
            # print('Precisa adicionar')
            insert_data(insert_query, [cit])
            data = retrieve_data(select_query, [cit])

        # pprint(data)
        citation_data.append(data)

    return citation_data

def insert_keywords(db, col_name, keywords):
    # print('\nKeywords (Done)')

    insert_query = """ INSERT INTO keywords (keyword) VALUES (%s)"""
    select_query = """ SELECT * FROM keywords WHERE keyword = %s"""

    keyword_data = []

    for kw in keywords:
        data = retrieve_data(select_query, [kw])
      
        if (data == None):
            # print('Precisa adicionar')
            insert_data(insert_query, [kw])
            data = retrieve_data(select_query, [kw])

        # pprint(data)
        keyword_data.append(data)

    return keyword_data

def insert_authors_articles(article, authors):
    # print('\nAuthors <-> Articles (Done)')

    insert_query = """ INSERT INTO authors_articles (fk_article, fk_author) VALUES (%s,%s)"""
    select_query = """ SELECT * FROM authors_articles WHERE fk_article = %s AND fk_author = %s"""

    for author in authors:
        data = retrieve_data(select_query,[article[0], author['id']])
      
        if (data == None):
            # print('Precisa adicionar')
            insert_data(insert_query, [article[0], author['id']])
            data = retrieve_data(select_query, [article[0], author['id']])

        # pprint(data)

def insert_articles_citations(article, citations):
    # print('\nArticles <-> Citations (Done)')

    insert_query = """ INSERT INTO articles_citations (fk_article, fk_citation) VALUES (%s,%s)"""
    select_query = """ SELECT * FROM articles_citations WHERE fk_article = %s AND fk_citation = %s"""

    for cit in citations:
        data = retrieve_data(select_query,[article[0], cit[0]])
      
        if (data == None):
            # print('Precisa adicionar')
            insert_data(insert_query, [article[0], cit[0]])
            data = retrieve_data(select_query, [article[0], cit[0]])

        # pprint(data)

def insert_articles_keywords(article, keywords):
    # print('\nArticles <-> Keywords (Done)')

    insert_query = """ INSERT INTO articles_keywords (fk_article, fk_keyword) VALUES (%s,%s)"""
    select_query = """ SELECT * FROM articles_keywords WHERE fk_article = %s AND fk_keyword = %s"""

    for key in keywords:
        data = retrieve_data(select_query,[article[0], key[0]])
      
        if (data == None):
            # print('Precisa adicionar')
            insert_data(insert_query, [article[0], key[0]])
            data = retrieve_data(select_query, [article[0], key[0]])

        # pprint(data)


def get_data(db, col_name, begin):
    collection = db[col_name + '_articles']

    count = begin

    for article in collection.find({}, no_cursor_timeout=True)[begin:]:
        if (article['title'] == ''): continue
        # pprint(article)

        venue     = insert_venue      (db, col_name, article['publication_id'])
        _article_ = insert_article    (db, col_name, article, venue)
        _authors_ = insert_authors    (db, col_name, article['_id'])
        keywords  = insert_keywords   (db, col_name, article['keywords'])
        citations = insert_citations  (db, col_name, article['references'])

        insert_authors_articles     (_article_, _authors_)
        insert_articles_citations   (_article_, citations)
        insert_articles_keywords    (_article_, keywords)

        # print('\n======================')
        
        # if (count % 10 == 0):
        print(count, '/ 200000 (?)')
        count += 1


def main():
    db = setup()
    # stats(db)

    col_name = 'ieeex'
    start = 0
    get_data(db, col_name, start)

if __name__ == "__main__": main()