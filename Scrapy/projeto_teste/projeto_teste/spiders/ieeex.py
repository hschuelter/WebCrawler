# scrapy crawl ieeex -o Data/x.json > Data/ieee.data
import scrapy
import json
import ast

class IEEEX_Spider(scrapy.Spider):
    name = "ieeex"
    start_urls = [  "https://ieeexplore.ieee.org/document/8540039",
                    "https://ieeexplore.ieee.org/document/6971171",
                    "https://ieeexplore.ieee.org/document/746625",
                    "https://ieeexplore.ieee.org/document/1425674" ]

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
                # print(m)
                meta = self.to_dict(m)

                return m, meta
        
        return '', ''

    ##############################################

    def extract_authors(self, metadata):
        key = 'authors'
        authors = []
        raw_data = metadata[key]
        
        for r in raw_data:
            author_info = dict()
            author = r['name']
            author = self.remove_tags(author)

            institution = r['affiliation']
            institution = self.remove_tags(institution)

            author_string = author
            if ( institution != "" ):
                author_string += " ( " + str(institution) + " )"
            authors.append( author_string )

        return authors
            
    def extract_title(self, metadata):
        key = 'title'
        title = metadata[key]
        title = self.remove_tags(title)
        return title

    def extract_abstract(self, metadata):
        key = 'abstract'
        abstract = metadata[key]
        abstract = abstract
        abstract = self.remove_tags(abstract)
        return abstract

    def extract_journal(self, metadata):
        key = 'displayPublicationTitle'
        journal = metadata[key]
        journal = self.remove_tags(journal)
        return journal

    def extract_date(self, metadata):
        key = 'journalDisplayDateOfPublication'
        date = metadata[key]
        date = self.remove_tags(date)
        return date

    def extract_num_pages(self, metadata):
        key_start = 'startPage'
        key_end   = 'endPage'
        start_page = metadata[key_start]
        end_page = metadata[key_end]

        num_pages = int(end_page) - int(start_page)
        return str(num_pages)

    def extract_doi(self, metadata):
        key = 'doi'
        doi = metadata[key]
        return doi

    def extract_keywords(self, metadata):
        key = 'keywords'
        array = metadata[key]

        keywords = []
        for a in array:
            for k in a['kwd']:
                keywords.append( k )

        return keywords

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


    def parse(self, response):
        #  o title
        #  o authors
        #  o abstract
        #  o conference/journal
        #  o date
        #  o pages
        #  o doi
        #  x isbn 
        #  x citations
        #  x downloads
        #  x references

        raw_metadata, metadata = self.extract_metadata(response)

        # self.print_metadata(metadata)

        article = dict()
        article['title']     = self.extract_title(metadata)
        article['authors']   = self.extract_authors(metadata)
        article['abstract']  = self.extract_abstract(metadata)
        article['journal']   = self.extract_journal(metadata)
        article['date']      = self.extract_date(metadata)
        article['num_pages'] = self.extract_num_pages(metadata)
        article['doi']       = self.extract_doi(metadata)
        article['keywords']  = self.extract_keywords(metadata)

        # conference = self.extract_conference(raw_metadata)
        # ids = self.extract_ids(raw_metadata)
        # isbn = self.extract_isbn(raw_metadata)

        ##############

        # references = self.extract_references(response)

        ##############

        ##############
        print("=========================")
        print("Authors: ")
        for a in article['authors']:
            print( '\t' + a )
        print("\nTitle: \"" + article['title'] + "\"")
        print("\nAbstract: \"" + article['abstract'] + "\"")
        print("Journal: \"" + article['journal'] + "\"")
        print("Date: \"" + article['date'] + "\"")
        print("Pages: \"" + article['num_pages'] + "\"")
        print("DOI: \"" + article['doi'] + "\"")
        print("Keywords: ", end="")
        print( article['keywords'] )

        print("=========================\n")

        # # for r in article_references:
        # #     print(">> " + r)
        # print("Num referencias: " + str(len(article_references)))
        # self.export(article_authors, article_title, article_abstract, article_conference, article_date, article_ids, article_pagerange, article_doi, article_isbn, article_total_citations, article_total_downloads, article_references)