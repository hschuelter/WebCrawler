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
        start_index = raw_metadata.find('"authors":[')
        
        stack = 0
        end_index = start_index        
        for ch in raw_metadata[start_index:]:
            if( ch == ']' and stack == 1):
                end_index += 1
                break
            
            if( ch == '[' ):
                stack += 1

            if( ch == ']' ):
                stack -= 1

            end_index += 1
            
        teste = raw_metadata[start_index : end_index]
        teste = teste.split( '{"name":"' )

        for i in range( 1, len(teste) ):
            info = teste[i].split( '","affiliation":"' )
            author = info[0]
            institution = info[1]
            
            index = 0
            for j in institution:
                if( j == '"'):
                    break
                index += 1

            institution = institution[:index]

            author_info = dict()
            author_info[ 'author' ] = author
            author_info[ 'institution' ] = institution

            author_string = author
            if ( institution != "" ):
                author_string += " ( " + str(institution) + " )"

            # authors.append( author_info )
            authors.append( author_string )
        
        # raw_metadata = raw_metadata[start_index:]
        # raw_metadata = raw_metadata.split('{"name":')
        
        # for raw_authors in raw_metadata[1:-1]:
        #     helper = raw_authors.split(',')[0]
        #     authors.append( helper.strip('"') )

        return authors

    def extract_title(self, raw_metadata):
        raw_title = raw_metadata.split(',')
        title = ""
        for rt in raw_title:
            if( '"title"' in rt ):
                title = rt
                break

        title = title.split(":")[1]
        title = title.strip('"')
        title = self.remove_tags(title)
        return title

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
                    
        abstract = abstract.split(":")[1]
        abstract = abstract.strip('"')
        abstract = self.remove_tags(abstract)
        return abstract

    def extract_journal(self, raw_metadata):
        raw_journal = raw_metadata.split(',')
        journal = ""
        for rt in raw_journal:
            if( '"displayPublicationTitle"' in rt ):
                journal = rt
                break

        journal = journal.split(":")[1]
        journal = journal.strip('"')
        journal = self.remove_tags(journal)
        return journal

    def extract_date(self, raw_metadata):
        raw_date = raw_metadata.split(',')
        date = ""
        for rt in raw_date:
            if( '"journalDisplayDateOfPublication"' in rt ):
                date = rt
                break

        date = date.split(":")[1]
        date = date.strip('"')
        date = self.remove_tags(date)
        return date

    def extract_num_pages(self, raw_metadata):
        raw_num_pages = raw_metadata.split(',')
        start_page = "?"
        end_page = "?"
        for rt in raw_num_pages:
            if( '"startPage"' in rt ):
                start_page = (rt.split(":")[1]).strip('"')
                start_page = self.remove_tags(start_page)
            if( '"endPage"' in rt ):
                end_page = (rt.split(":")[1]).strip('"')
                end_page = self.remove_tags(end_page)

        num_pages = int(end_page) - int(start_page)
        return str(num_pages)

    def extract_doi(self, raw_metadata):
        raw_doi = raw_metadata.split(',')
        doi = ""
        for rt in raw_doi:
            if( '"doi"' in rt ):
                doi = rt
                break

        doi = doi.split(":")[1]
        doi = doi.strip('"')
        return doi

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

        raw_metadata = self.extract_metadata(response)

        article = dict()
        article['title']     = self.extract_title(raw_metadata)        
        article['authors']   = self.extract_authors(raw_metadata)        
        article['abstract']  = self.extract_abstract(raw_metadata)        
        article['journal']   = self.extract_journal(raw_metadata)        
        article['date']      = self.extract_date(raw_metadata)        
        article['num_pages'] = self.extract_num_pages(raw_metadata)        
        article['doi']       = self.extract_doi(raw_metadata)
        article['keywords']  = self.extract_keywords(raw_metadata)

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
        print( ">>>>>>>>>>>>>>>>>>>>> ARRUMAR ISSO <<<<<<<<<<<<<<<<<<<<<" )
        print("Keywords: ", end="")
        print( article['keywords'] )

        print("=========================\n")

        # # for r in article_references:
        # #     print(">> " + r)
        # print("Num referencias: " + str(len(article_references)))
        # self.export(article_authors, article_title, article_abstract, article_conference, article_date, article_ids, article_pagerange, article_doi, article_isbn, article_total_citations, article_total_downloads, article_references)