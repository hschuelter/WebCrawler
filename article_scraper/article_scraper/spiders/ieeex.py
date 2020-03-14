# scrapy crawl ieeex -o Data/x.json > Data/ieee.data
# scrapy crawl ieeex > data/ieeex/10-ieeex.data
import html
import json
import psycopg2
import scrapy


class IEEEX_Spider(scrapy.Spider):
    name = "ieeex"
    
    start_urls = []
    with open("input/10-ieeex.links", "r") as f:
        start_urls = [url.strip() for url in f.readlines()]

    ##############################################

    def extract_metadata(self, response):
        metadata = []
        for raw_text in response.xpath("//script[@type='text/javascript']"):
            helper = raw_text.xpath("./text()").extract_first()
            if( (helper is not None) and ("global.document.metadata" in helper) ):
                metadata = helper.split('\n')
                break

        for m in metadata:
            if('global.document.metadata' in m):
                idx = m.find('{')
                m = m[idx:]
                meta = self.to_dict(m)

                return m, meta
        
        return '', ''

    ##############################################

    def extract_authors(self, metadata):
        key = 'authors'

        if key not in metadata:
            return []        

        authors = []
        raw_data = metadata[key]
        
        for r in raw_data:
            author_info = dict()

            author = r['name']
            author = self.remove_tags(author)
            author = html.unescape(author)
            author_info['name'] = author

            institute = r['affiliation']
            institute = self.remove_tags(institute)
            institute = html.unescape(institute)
            author_info['institute'] = institute

            authors.append( author_info )

        return authors
            
    def extract_title(self, metadata):
        key = 'title'
        
        if key not in metadata:
            return ""    


        title = metadata[key]
        title = self.remove_tags(title)
        title = html.unescape(title)
        return title

    def extract_abstract(self, metadata):
        key = 'abstract'
        
        if key not in metadata:
            return ""   

        abstract = metadata[key]
        abstract = abstract
        abstract = self.remove_tags(abstract)
        abstract = html.unescape(abstract)
        return abstract

    def extract_journal(self, metadata):
        key = 'displayPublicationTitle'

        if key not in metadata:
            return ""   
            
        journal = metadata[key]
        journal = self.remove_tags(journal)
        journal = html.unescape(journal)
        return journal

    def extract_date(self, metadata):
        key = 'chronOrPublicationDate'

        if key not in metadata:
            return ""   

        date = metadata[key]
        date = self.remove_tags(date)
        date = html.unescape(date)
        return date

    def extract_num_pages(self, metadata):
        key_start = 'startPage'
        key_end   = 'endPage'

        if ( (key_start not in metadata) or (key_end not in metadata)):
            return "0"

        start_page = metadata[key_start]
        end_page = metadata[key_end]

        try:
            num_pages = int(end_page) - int(start_page)
        except ValueError:
            num_pages = start_page + ' - ' + end_page
            pass

        return str(num_pages)

    def extract_doi(self, metadata):
        key = 'doi'

        if key not in metadata:
            return ""  

        doi = metadata[key]
        return doi

    def extract_keywords(self, metadata):
        key = 'keywords'

        if key not in metadata:
            return []        

        array = metadata[key]

        keywords = []
        for a in array:
            for kw in a['kwd']:
                k = html.unescape(kw) 
                keywords.append( k )

        return keywords

    def extract_publisher(self, metadata):
        key = 'publisher'

        if key not in metadata:
            return ""   

        publisher = metadata[key]
        publisher = self.remove_tags(publisher)
        publisher = html.unescape(publisher)
        return publisher

    ##############################################
    
    def remove_tags(self, string):
        stack = []
        aux = ""
        for i in range(0, len(string)):
            if( string[i] == '<' ):
                for j in range(i, len(string)):
                    aux = aux + string[j]
                    if( string[j] == '>'):
                        break
                
                stack.append( str(aux) )
                aux = ""

        for el in stack:
            string = string.replace(el,' ')

        return " ".join( string.split())

    def print_metadata(self, metadata):
        for key, value in metadata.items():
            print(key, '->', value)

    def to_dict(self, raw_metadata):
        raw_metadata = raw_metadata.strip(';')
        return json.loads(raw_metadata)

    ##############################################

    def insert_author(self, connection, table, author_name, author_institute):
        cur = connection.cursor()

        sql_string = "INSERT INTO " + table + (" (name, institute) VALUES (%s, %s)" % (author_name, author_institute) )
        cur.execute(sql_string)
        connection.commit()

        cur.close()

    def export_authors(self, authors):
        table = "ieee_authors"
        conn = psycopg2.connect(database='ieee_db', user='arthur', password='senha')
        cur = conn.cursor()
        
        for a in authors:
            name = a['name']
            institute = a['institute']
            select_query = 'SELECT author_id from %s WHERE name = %s AND institute = %s' % (table, name, institute)
            cur.execute(select_query)
            records = cur.fetchall()

            if(not bool(records)):
                self.insert_author(conn, table, name, institute)

        cur.close()
        conn.close()

        return ''

    def insert_articles(self, title, abstract, date, num_pages, journal, doi, keywords, publisher):
        table = "ieee_articles"

        conn = psycopg2.connect(database='ieee_db', user='arthur', password='senha')
        cur = conn.cursor()
        
        for i in range(0, len(keywords)):
            keywords[i] = keywords[i].replace("'", "`")
        keywords = "'" + ', '.join(keywords) + "'"

        select_query = '''
        select
            article_id,
            title,
            date,
            journal
        from 
            %s
        where
            title = %s AND
            date = %s  AND
            journal = %s AND
            doi = %s;''' % (table, title, date, journal, doi)
        cur.execute(select_query)
        records = cur.fetchall()

        if(not bool(records)):
            sql_string = "INSERT INTO " + table + (" (title, abstract, date, num_pages, journal, doi, keywords, publisher) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" % (title, abstract, date, num_pages, journal, doi, keywords, publisher) )
            cur.execute(sql_string)
            conn.commit()

        cur.close()
        conn.close()

        return ''

    def insert_authors_articles(self, authors, title, date, journal, doi):
        table_authors  = "ieee_authors"
        table_articles = "ieee_articles"
        conn = psycopg2.connect(database='ieee_db', user='arthur', password='senha')
        cur = conn.cursor()

        article_id = -1
        select_articles_query = '''
        select
            article_id
        from 
            %s
        where
            title = %s AND
            date = %s  AND
            journal = %s AND
            doi = %s;''' % (table_articles, title, date, journal, doi)
        
        cur.execute(select_articles_query)
        records = cur.fetchall()
        if(bool(records)):
            article_id = records[0][0]

        author_id = []
        for a in authors:
            name = a['name']
            institute = a['institute']
            
            select_authors_query = 'SELECT author_id from %s WHERE name = %s AND institute = %s' % (table_authors, name, institute)
            cur.execute(select_authors_query)
            records = cur.fetchall()

            if(bool(records)):
                author_id.append(records[0][0])

        if(article_id != -1):
            table = "ieee_authors_articles"
            for au_id in author_id:
                select_authors_articles_query = 'SELECT fk_article FROM %s WHERE fk_article = %s AND fk_author = %s' % (table, article_id, au_id)
                cur.execute(select_authors_articles_query)
                records = cur.fetchall()
                # print(select_authors_articles_query)
                # print(records)
                if(not bool(records)):
                    sql_string = "INSERT INTO %s (fk_article, fk_author) VALUES (%s, %s)" % (table, article_id, au_id)
                    cur.execute(sql_string)
                    conn.commit()

        cur.close()
        conn.close()


    ##############################################

    def parse(self, response):
        # o title
        # o authors
        # o abstract
        # o conference/journal
        # o date
        # o pages
        # o doi
        # x citations
        # x references

        raw_metadata, metadata = self.extract_metadata(response)

        article = dict()
        article['title']     = self.extract_title(metadata)
        article['authors']   = self.extract_authors(metadata)
        article['abstract']  = self.extract_abstract(metadata)
        article['journal']   = self.extract_journal(metadata)
        article['date']      = self.extract_date(metadata)
        article['num_pages'] = self.extract_num_pages(metadata)
        article['doi']       = self.extract_doi(metadata)
        article['keywords']  = self.extract_keywords(metadata)
        article['publisher'] = self.extract_publisher(metadata)
        
        article['link'] = response.request.url

        ##############
        print("=========================")
        print('Link:', response.request.url)
        print("Authors: ")
        for a in article['authors']:
            print( '\t' + a['name'] + '( ' + a['institute'] + ' )' )
        print("\nTitle: \"" + article['title'] + "\"")
        print("\nAbstract: \"" + article['abstract'] + "\"")
        print("Journal: \"" + article['journal'] + "\"")
        print("Date: \"" + article['date'] + "\"")
        print("Pages: \"" + article['num_pages'] + "\"")
        print("DOI: \"" + article['doi'] + "\"")
        print("Publisher: \"" + article['publisher'] + "\"")
        print("Keywords: ", end="")
        print( article['keywords'] )

        print(article)

        print("=========================\n")


        ############
        
        # article['title']       = "'" + article['title'].replace("'", "`") + "'"
        
        # for i in range(0, len(article['authors'])):
        #     article['authors'][i]['name']       = "'" + article['authors'][i]['name'].replace("'", "`") + "'"
        #     article['authors'][i]['institute']  = "'" + article['authors'][i]['institute'].replace("'", "`") + "'"

        # article['abstract']    = "'" + article['abstract'].replace("'", "`") + "'"
        # article['date']        = "'" + article['date'].replace("'", "`") + "'"
        # article['num_pages']   = "'" + str(article['num_pages']) + "'"
        # article['journal']     = "'" + article['journal'].replace("'", "`") + "'"
        # article['doi']         = "'" + article['doi'] + "'"
        # article['publisher']         = "'" + article['publisher'] + "'"

        # for i in range(0, len(article['keywords'])):
        #     article['keywords'][i]= "'" + article['keywords'][i].replace("'", "`") + "'"


        # self.export_authors(article['authors'])
        # if(not article['title'].replace(' ', '') == ''):
        #     self.insert_articles(article['title'], article['abstract'], article['date'], article['num_pages'], article['journal'], article['doi'], article['keywords'], article['publisher'])
        
        # self.insert_authors_articles(article['authors'], article['title'], article['date'], article['journal'], article['doi'])
