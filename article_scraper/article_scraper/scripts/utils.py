import pprint
import pymongo

from bson.objectid import ObjectId

pp = pprint.PrettyPrinter(indent=4)

def pprint(text):
    pp.pprint(text)

def dict_print(d):
    for key in d:
        print('\t', key, ':', d[key])

def stats(db):
    
    print('Articles:')
    collection_names = ['acm_articles', 'ieeex_articles', 'springer_articles', 'springer_chapters_articles']
    abstract = ''
    date = ''
    doi = ''
    journal = ''
    keywords = ''
    link = ''
    pages = ''
    references = ''
    title = ''

    for col_name in collection_names:
        for article in db[col_name].find():
            if (article['abstract'] != None):
                if (len(article['abstract']) > len(abstract)): abstract = article['abstract']

            if (article['date'] != None):
                if (len(article['date']) > len(date)): date = article['date']

            if (article['doi'] != None):
                if (len(article['doi']) > len(doi)): doi = article['doi']

            if (article['journal'] != None):
                if (len(article['journal']) > len(journal)): journal = article['journal']
            
            if (article['link'] != None):
                if (len(article['link']) > len(link)): link = article['link']

            if (article['pages'] != None):
                if (len(str(article['pages'])) > len(str(pages))): pages = article['pages']

            article['title'] = ' '.join(article['title'].split())
            if (len(article['title']) > len(title)): title = article['title']
            
            for ref in article['references']:
                if (len(ref) > len(references)): references = ref

            for kw in article['keywords']:
                if (len(kw) > len(keywords)): keywords = kw

    print('abstract:', len(abstract))
    print('date:', len(date))
    print('doi:', len(doi))
    print('journal:', len(journal))
    print('link:', len(link))
    print('pages:', len(pages))
    print('title:', len(title))
    print('keywords:', len(keywords))
    print('references:', len(references))


    print('\nAuthors:')
    collection_names = ['acm_authors', 'ieeex_authors', 'springer_authors', 'springer_chapters_authors']
    name = ''
    institute = ''
    for col_name in collection_names:
        for author in db[col_name].find():
            author['name'] = ' '.join(author['name'].split('\n'))
            author['name'] = ' '.join(author['name'].split())

            if (len(author['name']) > len(name)): name = author['name']
            if (len(author['institute']) > len(institute)): institute = author['institute']

    print('Name:', len(name))
    print('Institute:', len(institute))
    
    print('\nPublishers:')
    collection_names = ['acm_publications', 'ieeex_publications', 'springer_publications', 'springer_chapters_publications']
    title = ''
    publisher = ''
    url = ''
    for col_name in collection_names:
        for publication in db[col_name].find():
            publication['publisher'] = ' '.join(publication['publisher'].split())

            if (len(publication['title']) > len(title)): title = publication['title']
            if (len(publication['publisher']) > len(publisher)): publisher = publication['publisher']
            if (len(publication['url']) > len(url)): url = publication['url']

    print('Title:', len(title), '-', title)
    print('Publisher:', len(publisher))
    print('Url:', len(url))
    