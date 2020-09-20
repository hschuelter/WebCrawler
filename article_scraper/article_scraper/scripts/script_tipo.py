# python3 script_tipo.py
from psycopg2 import connect, sql

from bson.objectid import ObjectId
from utils import pprint, sanitize

import json
import logging, sys
import re
import requests
import time
import html as ht



from functools import reduce
from lxml import html


connection = connect ( user="arthur",
                        password="senha",
                        host="127.0.0.1",
                        port="5432",
                        database="venues_db")
cursor = connection.cursor()

def retrieve_data(select_query, input_):
    input_ = list(map(lambda x: sanitize(str(x)), input_))
    cursor.execute(select_query, input_)
    data = cursor.fetchone()

    return data


def update_data(update_query, input_):
    input_ = list(map(lambda x: sanitize(str(x)), input_))
    cursor.execute(update_query, input_)
    connection.commit()


select_query_tipo = """
    SELECT title
    FROM articles 
    WHERE
        article_id = %s; """


select_query_venue = """
    select
        ar.title, 
        ar.tipo, 
        ve.venue_id,
        ve.title,
        ve.tipo,
        ve.venue_id
    from
        articles ar
        inner join 
            venues ve
            on ve.venue_id  = ar.fk_venue 
    where
        ar.article_id = %s and
        ve.tipo is null;
 """

select_query_date = """
    SELECT "date"
    FROM articles 
    WHERE
        article_id = %s; """


select_query_keywords = """
SELECT 
    array_agg(kw.keyword)
FROM
    keywords kw
INNER JOIN
    articles_keywords ak
    ON ak.fk_keyword = kw.keyword_id
INNER JOIN 
	articles ar
	on ar.article_id = ak.fk_article 
WHERE
    article_id = %s;
"""

update_query_tipo = """
    UPDATE articles
    SET 
        tipo = %s
    WHERE
	    article_id = %s;
    """

update_query_venue = """
    UPDATE venues
    SET 
        tipo = %s
    WHERE
	    venue_id = %s;
    """

update_query_keywords = """
    UPDATE articles
    SET 
        keywords = %s
    WHERE
	    article_id = %s;
    """

update_query_date = """
    UPDATE articles
    SET 
        date_formatted = %s
    WHERE
	    article_id = %s;
    """
def limpar(q):
    s = re.sub('[^0-9a-zA-Z]+', ' ', s)
    return s

def make_query(q):
    data = {}
    base = 'https://dblp.org/search/publ/api?'
    search = 'q=' + '+'.join(limpar(q).split(' '))
    form = '&format=json'
    hit = '&h=1'

    data['url'] = base + search + form + hit
    print(data['url'])

    r = requests.get(data['url'])
    print(r.status_code)
    d = r.json()['result']
    print(d)

    if (limpar(q) == ' '):
        return
    if (int(d['hits']['@total']) == 0):
        return ''

    hits = d['hits']['hit']
    for h in hits:
        data['type'] = h['info']['type']
        pprint(data)
        return data['type']

def convert_date(_date_):
    d = get_day(_date_)
    m = get_month(_date_)
    y = get_year(_date_)
    if (y == '█'):
        return ''
    return y + '-' + m + '-' + d

def get_day(_date_):
    d = _date_.lower().split(" ")
    month = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']


    _d = d[0]

    for i in range (len(month)):
        if ((month[i] in _d) or (meses[i] in _d)):
            return '01'


    years = list(range(1900, 2100))
    for y in years:
        _y_ = str(y)
        if (_y_ in d[0]):
            return '01'
    
    flag = True
    coisa = list(range(1, 32))
    for c in coisa:
        c_ = str(c)
        if (c_ in d[0]):
            flag = False

    if (flag):
        return "01"


    if ('-' in d[0]):
        new_d = d[0].split('-')[0]
        if (len(new_d) == 1):
            return "0" + new_d
        return new_d

    return d[0][0:2]

def get_month(_date_):
    month = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

    _d = _date_.lower() 

    coisa = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

    if ('firstquarter' in _d):
        return "01"
    
    if ('secondquarter' in _d):
        return "04"

    if ('thirdquarter' in _d):
        return "07"

    if ('fourthquarter' in _d):
        return "10"
    

    for i in range (len(month)):
        if ((month[i] in _d) or (meses[i] in _d)):
            return coisa[i]
    return '01'

def get_year(_date_):
    years = list(range(1900, 2100))
    for y in years:
        _y_ = str(y)
        if (_y_ in _date_):
            return _y_
    return '█'


def venue_tipo(result):
    ar_title = result[0]
    ar_tipo = result[1]
    ve_venue_id = result[2]
    ve_title = result[3]
    ve_tipo = result[4]
    ve_id = result[5]

    print("\tar_title", result[0])
    print("\tar_tipo", result[1])
    print("\tve_venue_id", result[2])
    print("\tve_title", result[3])
    print("\tve_tipo", result[4])
    print("\tve_id", result[5])

    venue_tipo = ''
    if (ar_tipo == 'Conference and Workshop Papers'):
        venue_tipo = 'Conference'
    elif (ar_tipo == 'Journal Articles'):
        venue_tipo = 'Journal'

    return venue_tipo, int(result[5])

def main():
    start = 100000
    end   = 250000
    # end   = 250000
    for idx in range(start, end):
        result = retrieve_data(select_query_venue, [idx])
        if (not result == None and result[0] != ""):
            # d = convert_date(result[0])
            print(idx)
            ve, ve_idx = venue_tipo(result)
            if (result[4] == None):
                print(ve)
            if (not ve == '' ):
                update_data(update_query_venue, [ve, ve_idx])
        
        #     words = ' '.join(result[0]).lower().split()
        #     keywords = " ".join(sorted(set(words), key=words.index))
        #     print (keywords)
        #     print(idx, '/', end)

        #     # tipo = make_query(result[0])
        #     if (not keywords == None):
        #     print('=====================')


if __name__ == "__main__": main()