# python3 script_ihc.py
from psycopg2 import connect, sql

from bson.objectid import ObjectId
from utils import dict_print, pprint, sanitize, stats

import json
import pandas

connection = connect (  user="arthur",
                        password="senha",
                        host="127.0.0.1",
                        port="5432",
                        database="venues_db")
cursor = connection.cursor()

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

def insert_article(article, venue):
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
        article['title'],   article['abstract'],    article['pages'],                   article['date'],
        article['doi'],     article['link'],        "Conference and Workshop Papers",   fk_venue
    ]
    data = retrieve_data(select_query, article_input)
    
    if (data == None):
        print('\tPrecisa adicionar... ')
        insert_data(insert_query, article_input)
        data = retrieve_data(select_query, article_input)

    print('\tArticle:', data)
    return data

def insert_authors(author_list):
    authors = []
    authors_ids = []

    insert_query = """ INSERT INTO authors (name, institute) VALUES (%s,%s)"""
    select_query = """ SELECT * FROM authors WHERE name = %s AND institute = %s """


    # print("\nAuthors (Done) ")
    for this_author in author_list:
        if (type(this_author['institute']) == list):
            this_author['institute'] = ", ".join(this_author['institute'])
        
        data = retrieve_data(select_query, [this_author['name'], this_author['institute']])

        if (data == None):
            print("\tPrecisa adicionar...")
            insert_data(insert_query, [this_author['name'], this_author['institute']])
            data = retrieve_data(select_query, [this_author['name'], this_author['institute']])

        print('\tAuthor:', data)
        this_author['id'] = data[0]
        authors.append(this_author)

    return authors

def insert_venue(venue):
    # print("\nVenue (Done)")

    insert_query = """ INSERT INTO venues (title, publisher, link) VALUES (%s,%s,%s)"""
    select_query = """ SELECT * FROM venues WHERE title = %s AND publisher = %s AND link = %s"""

    data = retrieve_data(select_query, [venue['title'], venue['publisher'], venue['url']])
    
    if (data == None):
        print('\tPrecisa adicionar...')
        insert_data(insert_query, [venue['title'], venue['publisher'], venue['url']])
        data = retrieve_data(select_query, [venue['title'], venue['publisher'], venue['url']])

    print('\tVenue:', data)
    return data
    
def insert_citations(citations):
    # print('\nCitations')

    insert_query = """ INSERT INTO citations (citation) VALUES (%s)"""
    select_query = """ SELECT * FROM citations WHERE citation = %s"""

    citation_data = []

    for cit in citations:
        data = retrieve_data(select_query, [cit])
      
        if (data == None):
            print('\tPrecisa adicionar...')
            insert_data(insert_query, [cit])
            data = retrieve_data(select_query, [cit])

        print('\tCit:', data)
        citation_data.append(data)

    return citation_data

def insert_keywords(keywords):
    # print('\nKeywords (Done)')

    insert_query = """ INSERT INTO keywords (keyword) VALUES (%s)"""
    select_query = """ SELECT * FROM keywords WHERE keyword = %s"""

    keyword_data = []

    for kw in keywords:
        data = retrieve_data(select_query, [kw])
      
        if (data == None):
            print('\tPrecisa adicionar...')
            insert_data(insert_query, [kw])
            data = retrieve_data(select_query, [kw])

        print('\tKW:', data)
        keyword_data.append(data)

    return keyword_data

def insert_authors_articles(article, authors):
    # print('\nAuthors <-> Articles (Done)')

    insert_query = """ INSERT INTO authors_articles (fk_article, fk_author) VALUES (%s,%s)"""
    select_query = """ SELECT * FROM authors_articles WHERE fk_article = %s AND fk_author = %s"""

    for author in authors:
        data = retrieve_data(select_query,[article[0], author['id']])
      
        if (data == None):
            print('\tPrecisa adicionar...')
            insert_data(insert_query, [article[0], author['id']])
            data = retrieve_data(select_query, [article[0], author['id']])

        print('\tAA:', data)

def insert_articles_citations(article, citations):
    # print('\nArticles <-> Citations (Done)')

    insert_query = """ INSERT INTO articles_citations (fk_article, fk_citation) VALUES (%s,%s)"""
    select_query = """ SELECT * FROM articles_citations WHERE fk_article = %s AND fk_citation = %s"""

    for cit in citations:
        data = retrieve_data(select_query,[article[0], cit[0]])
      
        if (data == None):
            print('\tPrecisa adicionar...')
            insert_data(insert_query, [article[0], cit[0]])
            data = retrieve_data(select_query, [article[0], cit[0]])

        print('\tAC:', data)

def insert_articles_keywords(article, keywords):
    # print('\nArticles <-> Keywords (Done)')

    insert_query = """ INSERT INTO articles_keywords (fk_article, fk_keyword) VALUES (%s,%s)"""
    select_query = """ SELECT * FROM articles_keywords WHERE fk_article = %s AND fk_keyword = %s"""

    for key in keywords:
        data = retrieve_data(select_query,[article[0], key[0]])
      
        if (data == None):
            print('\tPrecisa adicionar...')
            insert_data(insert_query, [article[0], key[0]])
            data = retrieve_data(select_query, [article[0], key[0]])

        print('\tAK:', data)


def verify_title(article):
    select_query = """
    SELECT * 
    FROM articles 
    WHERE
        title = %s"""

    
    article_input = [ article['title'] ]
    data = retrieve_data(select_query, article_input)
    
    if (data == None):
        return False
    return True

def get_data(data):
    count = 0

    for article in data:
        print(count, end=' ')
        count += 1
        if (article['title'] == ''): continue

        # if (count < 37970):
        #     print('next')
        #     continue

        if (verify_title(article)):
            print('next')
            continue
        print('add')
        # pprint(article)

        venue     = insert_venue      (article['venue'])
        _article_ = insert_article    (article, venue)
        _authors_ = insert_authors    (article['authors'])
        keywords  = insert_keywords   (article['keywords'])
        citations = insert_citations  (article['references'])

        insert_authors_articles     (_article_, _authors_)
        insert_articles_citations   (_article_, citations)
        insert_articles_keywords    (_article_, keywords)

        print('\n======================')


def main():
    data = []
    fp = '../output/ban/springer-chapters.data'
    with open(fp, "r") as f:
        data = [json.loads(datum) for datum in f.readlines()]

    # keywords = []
    # references = []
    # link = []
    # title = []
    # abstract = []
    # authors = []
    # pages = []
    # doi = []
    # venue = []
    # date = []

    # for d in data:
    #     keywords.append(d['keywords'])
    #     venue.append(d['venue']['title'])
    #     link.append(d['link'])
    #     title.append(d['title'])
    #     abstract.append(d['abstract'])
    #     authors.append(d['authors'])
    #     pages.append(d['pages'])
    #     doi.append(d['doi'])

    # data_final = {
    #     'Title': title,
    #     'Abstract': abstract,
    #     'Authors': authors,
    #     'Pages': pages,
    #     'Venue': venue,
    #     'Doi': doi,
    #     'Date': date,
    #     'Link': link,
    #     'Keywords': keywords
    # }

    # df = pandas.DataFrame.from_dict(data_final, orient='index')
    # df.to_csv('ihc-2011.csv')
    # with open('ihc-2006.json', 'w') as outfile:
    #     json.dump(d, outfile)
    # print(d)
    # for d in data:
    #     print(d)
    # start = 0
    get_data(data)

if __name__ == "__main__": main()