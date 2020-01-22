# scrapy crawl ieeex -o Data/x.json > Data/ieee.data
import scrapy

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
                return m
        
        return ''

    def extract_authors(self, raw_metadata):
        authors = []
        index_start = raw_metadata.find('"authors":[')

        raw_metadata = raw_metadata[index_start:]
        raw_metadata = raw_metadata.split('{"name":')
        
        for raw_authors in raw_metadata[1:-1]:
            helper = raw_authors.split(',')[0]
            authors.append( helper.strip('"') )

        return authors

    def extract_title(self, raw_metadata):
        raw_title = raw_metadata.split(',')
        title = ""
        for rt in raw_title:
            if( '"title"' in rt ):
                title = rt
                break

        helper = title.split(":")[1]
        return helper.strip('"')

    def extract_abstract(self, raw_metadata):
        raw_abstract = raw_metadata.split(',')
        abstract = ""
        for i in range(0, len(raw_abstract)-1):
            if( '"abstract"' in raw_abstract[i] and raw_abstract[i].index('"abstract"') == 0  ):
                abstract = raw_abstract[i]
                j = i
                while( raw_abstract[j][-1] != '"' ):
                    j += 1
                    abstract += raw_abstract[j]

                break
                    
        helper = abstract.split(":")[1]
        return helper.strip('"')

    def extract_journal(self, raw_metadata):
        raw_journal = raw_metadata.split(',')
        journal = ""
        for rt in raw_journal:
            if( '"displayPublicationTitle"' in rt ):
                journal = rt
                break

        helper = journal.split(":")[1]
        return helper.strip('"')

    def extract_date(self, raw_metadata):
        raw_date = raw_metadata.split(',')
        date = ""
        for rt in raw_date:
            if( '"journalDisplayDateOfPublication"' in rt ):
                date = rt
                break

        helper = date.split(":")[1]
        return helper.strip('"')

    def extract_num_pages(self, raw_metadata):
        raw_num_pages = raw_metadata.split(',')
        start_page = "?"
        end_page = "?"
        for rt in raw_num_pages:
            if( '"startPage"' in rt ):
                start_page = (rt.split(":")[1]).strip('"')
            if( '"endPage"' in rt ):
                end_page = (rt.split(":")[1]).strip('"')

        num_pages = int(end_page) - int(start_page)
        return num_pages

    def extract_doi(self, raw_metadata):
        raw_doi = raw_metadata.split(',')
        doi = ""
        for rt in raw_doi:
            if( '"doi"' in rt ):
                doi = rt
                break

        helper = doi.split(":")[1]
        return helper.strip('"')


    def extract_keywords(self, raw_metadata):
        raw_keywords = raw_metadata.split(',')
        ieee_helper = ""
        authors_keywords = ""

        for i in range(0, len(raw_keywords)-1):
            if( 'IEEE Keywords' in raw_keywords[i] ):
                aux = raw_keywords[i]
                j = i
                while( not (']}' in raw_keywords[j]) ):
                    j += 1
                    aux += ', ' + raw_keywords[j]
                ieee_helper = aux
                break

        for i in range(0, len(raw_keywords)-1):
            if( 'Author Keywords' in raw_keywords[i] ):
                aux = raw_keywords[i]
                j = i
                while( not (']}]' in raw_keywords[j]) ):
                    j += 1
                    aux += ', ' + raw_keywords[j]
                authors_keywords = aux
                break

        all_keywords = []

        ieee_keywords = ieee_helper.split('"kwd"')[1]
        ieee_keywords = (ieee_keywords[2:-2])
        for kwd in ieee_keywords.split(", "):
            aux = kwd.strip('"').lower()
            if ( not aux in all_keywords ):
                all_keywords.append( aux )

        if( authors_keywords != ""):
            authors_keywords = authors_keywords.split('"kwd"')[1]
            authors_keywords = (authors_keywords[2:-3])
            for kwd in authors_keywords.split(", "):
                aux = kwd.strip('"').lower()
                if ( not aux in all_keywords ):
                    all_keywords.append( aux )

        return all_keywords

    ##############################################

    def parse(self, response):
        #  o title
        #  o authors
        #  o abstract
        #  o conference/journal
        #  x date
        #  x ids
        #  x pages
        #  o doi
        #  x isbn 
        #  x citations
        #  x downloads
        #  x references

        raw_metadata = self.extract_metadata(response)
        
        title = self.extract_title(raw_metadata)
        authors = self.extract_authors(raw_metadata)
        abstract = self.extract_abstract(raw_metadata)
        journal = self.extract_journal(raw_metadata)
        date = self.extract_date(raw_metadata)
        num_pages = self.extract_num_pages(raw_metadata)
        doi = self.extract_doi(raw_metadata)

        keywords = self.extract_keywords(raw_metadata)

        # conference = self.extract_conference(raw_metadata)
        # ids = self.extract_ids(raw_metadata)
        # isbn = self.extract_isbn(raw_metadata)

        ##############

        # references = self.extract_references(response)

        ##############
        print("=========================")
        print("Authors: ", end="")
        print(authors)
        print("\nTitle: \"" + title + "\"")
        print("\nAbstract: \"" + abstract + "\"")
        print("Journal: \"" + journal + "\"")
        print("Date: \"" + date + "\"")
        print("Pages: \"" + str(num_pages) + "\"")
        print("DOI: \"" + doi + "\"")
        print("Keywords: ", end="")
        print(keywords)

        # print("ISBN: \"" + isbn + "\"")
        print("=========================\n")
        # # for r in article_references:
        # #     print(">> " + r)
        # print("Num referencias: " + str(len(article_references)))
        # self.export(article_authors, article_title, article_abstract, article_conference, article_date, article_ids, article_pagerange, article_doi, article_isbn, article_total_citations, article_total_downloads, article_references)