# scrapy crawl ieeex -o Data/teste.json
import scrapy

class IEEEX_Spider(scrapy.Spider):
    name = "ieeex"
    start_urls = [ "https://ieeexplore.ieee.org/document/8540039" ]

    ##############################################

    def get_authors(self, response):
        authors = []
        # //a[@_ngcontent-c32]/span/text()

        print("Authors: ")
        for author_raw in response.xpath('//a[@_ngcontent-c7]/span'):
            content = author_raw.xpath('./text()').extract_first()
            authors.append(content)

        return authors

    def get_title(self, response):
        title = []
        for title_raw in response.xpath("//script[@type='text/javascript']"):
            # if("global.document.metadata" in title_raw.extract_first() ):
            helper = title_raw.xpath("./text()").extract_first()
            if( (helper is not None) and ("global.document.metadata" in helper) ):
                title = helper.split('\n')
                # print(title)
                break

        # helper = helper.split('\n')
        while('' in title):
            title.remove('')

        title_scraped = ""
        for e in title:
            for es in e.split(','):
                if( '"title"' in es ):
                    title_scraped = es
                    break

            if(title_scraped != ""):
                break

        return title_scraped.split(':')[1]

    ##############################################

    def parse(self, response):

        # print("###############")
        # print(response.body)
        # print("###############")
        
        # article_authors = self.get_authors(response)
        # print(article_authors)

        article_title = self.get_title(response)
        # print(article_title)

        print("BBBBBBBBBBBBB")

        # article_abstract = self.get_abstract(response)
        # article_conference = self.get_conference(response)
        # article_date = self.get_date(response)
        # article_ids = self.get_ids(response)
        # article_pagerange = self.get_pagerange(response)
        # article_doi = self.get_doi(response)
        # article_isbn = self.get_isbn(response)

        ##############

        # article_total_citations = self.get_total_citations(response)
        # article_total_downloads = self.get_total_downloads(response)
        # article_references = self.get_references(response)

        ##############
        print("=========================")
        # print("Authors: ", end="")
        # print(article_authors)
        print("Title: \"" + article_title + "\"")
        # print("Abstract: \"" + article_abstract + "\"")
        # print("Conference: \"" + article_conference + "\"")
        # print("Date: \"" + article_date + "\"")
        # print("IDS: \"" + article_ids + "\"")
        # print("Page range: \"" + article_pagerange + "\"")
        # print("DOI: \"" + article_doi + "\"")
        # print("ISBN: \"" + article_isbn + "\"")
        # print("Total Citations: \"" + article_total_citations + "\"")
        # print("Total Downloads: \"" + article_total_downloads + "\"")
        print("=========================")
        # # for r in article_references:
        # #     print(">> " + r)
        # print("Num referencias: " + str(len(article_references)))
        # self.export(article_authors, article_title, article_abstract, article_conference, article_date, article_ids, article_pagerange, article_doi, article_isbn, article_total_citations, article_total_downloads, article_references)