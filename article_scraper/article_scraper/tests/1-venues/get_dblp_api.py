import json
import logging, sys
import re
import requests
import time
import html as ht

from functools import reduce
from lxml import html

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    with open('venues-bd.txt', 'r') as f:
        venues = [v.strip().lower() for v in f.readlines()]

    
    for v in venues:
        log()

        v = v.split()
        base = 'https://dblp.org/search/publ/api?'
        search = 'q=' + '+'.join(v)
        form = '&format=json'

        url = base + search + form
        print(url)

        r = requests.get(url)
        d = r.json()['result']


        if (int(d['hits']['@total']) == 0):
            continue

        hits = d['hits']['hit']
        for h in hits:
            print_data(h)
        

def log():
    logging.debug('========= Começando uma venue =========')
    time.sleep(3)


def print_data(data):
    new_data = {}

    url = data['info']['url']

    new_data['title'] = ht.unescape(data['info']['title'])
    new_data['score'] = data['@score']
    new_data['url'] = get_url(url)

    print(json.dumps(new_data))

def get_url(old_url):
    page = requests.get(old_url)
    html_tree = html.fromstring(page.content)

    xpath_string = "//a/@href"
    url = html_tree.xpath(xpath_string)

    url = list(filter(lambda x : 
                ('https://dblp.org/db/journals/' in x and x > 'https://dblp.org/db/journals/') or
                ('https://dblp.org/db/conf/'     in x and x > 'https://dblp.org/db/conf/'), url))

    url = list(dict.fromkeys(url))
    url = ''.join(url)

    return url


if __name__ == "__main__": main()