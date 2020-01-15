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
        for author_raw in response.xpath('//a[@_ngcontent-c32]/span/'):
            content = author_raw.xpath('./text()').extract_first()
            authors.append(content)

        return authors

    def get_title(self, response):
        title = ""
        for author_raw in response.xpath('//title'):
            title = author_raw.xpath('./text()').extract_first()
            break

        return title


    ##############################################

    def parse(self, response):
        
        article_authors = self.get_authors(response)
        print(article_authors)

        article_title = self.get_title(response)
        print(article_title)

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
        # print("=========================")
        # print("Authors: ", end="")
        # print(article_authors)
        # print("Title: \"" + article_title + "\"")
        # print("Abstract: \"" + article_abstract + "\"")
        # print("Conference: \"" + article_conference + "\"")
        # print("Date: \"" + article_date + "\"")
        # print("IDS: \"" + article_ids + "\"")
        # print("Page range: \"" + article_pagerange + "\"")
        # print("DOI: \"" + article_doi + "\"")
        # print("ISBN: \"" + article_isbn + "\"")
        # print("Total Citations: \"" + article_total_citations + "\"")
        # print("Total Downloads: \"" + article_total_downloads + "\"")
        # print("=========================")
        # # for r in article_references:
        # #     print(">> " + r)
        # print("Num referencias: " + str(len(article_references)))
        # self.export(article_authors, article_title, article_abstract, article_conference, article_date, article_ids, article_pagerange, article_doi, article_isbn, article_total_citations, article_total_downloads, article_references)