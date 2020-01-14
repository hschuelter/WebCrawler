# scrapy crawl acm -o Data/teste.json
import scrapy

class ACM_Spider(scrapy.Spider):
    name = "acm"
    start_urls = [
        "https://dl.acm.org/doi/10.1145/3357155.3358455", # "A proposal to ..." (IHC 2019)
        "https://dl.acm.org/doi/10.1145/3357155.3358468", # "A study on ..."    (IHC 2019)
        "https://dl.acm.org/doi/10.1145/3357155.3358485", # "A survey on ..."   (IHC 2019)
        "https://dl.acm.org/doi/10.1145/3357155.3358446", # "A platform ..."    (IHC 2019)
        "https://dl.acm.org/doi/10.1145/3274192.3274197", # "Adaptation ..."    (IHC 2018)
        "https://dl.acm.org/doi/10.1145/3274192.3274204", # "CoDesign in ..."   (IHC 2018)
        "https://dl.acm.org/doi/10.1145/3274192.3274209", # "Do I Know What..." (IHC 2018)
        "https://dl.acm.org/doi/10.1145/3160504.3160506", # "A Scenario..."     (IHC 2017)
        "https://dl.acm.org/doi/10.1145/3160504.3160533", # "Best practices..." (IHC 2017)
        "https://dl.acm.org/doi/10.1145/3160504.3160542", # "Designing..."      (IHC 2017)
        "https://dl.acm.org/doi/10.1145/3160504.3160512"  # "A Systematic..."   (IHC 2017)
     ]
    # "https://dl.acm.org/doi/10.1145/3357155.3358455" -> "A proposal to adapt..."  (IHC 2019)
    # "https://dl.acm.org/doi/10.1145/3160504.3160512" -> "A Systematic Mapping..." (IHC 2017) 


    def get_authors(self, response):
        authors = []
        for author_names_raw in response.xpath("//a[@class='author-name']"):
            author_name = author_names_raw.xpath("./@title").extract_first()

            if (author_name not in authors):
                authors.append(author_name)
        
        return authors

    def get_title(self, response):
        title = ""
        for titles_raw in response.xpath("//h1[@class='citation__title']"):
            title_scraped = titles_raw.xpath("./text()").extract_first()
            title = title_scraped.strip()
        
        return title

    def get_abstract(self, response):
        abstract = ""
        for abstract_raw in response.xpath("//div[@class='article__section article__abstract hlFld-Abstract']/p"):
            abstract_scraped = abstract_raw.xpath("./text()").extract_first()
            abstract = abstract_scraped.strip()

        return abstract

    def get_conference(self, response):
        conference = ""
        for conference_raw in response.xpath("//span[@class='epub-section__title']"):
            conference_scraped = conference_raw.xpath("./text()").extract_first()
            conference = conference_scraped.strip()

        return conference

    def get_date(self, response):
        date = ""
        for dates_raw in response.xpath("//span[@class='epub-section__date']"):
            date_scraped = dates_raw.xpath("./text()").extract_first()
            date = date_scraped.strip()

        return date

    def get_ids(self, response):
        ids = ""
        for ids_raw in response.xpath("//span[@class='epub-section__ids']"):
            ids_scraped = ids_raw.xpath("./text()").extract_first()
            ids = ids_scraped.strip()
        
        return ids

    def get_pagerange(self, response):
        pagerange = ""
        for pagerange_raw in response.xpath("//span[@class='epub-section__pagerange']"):
            pagerange_scraped = pagerange_raw.xpath("./text()").extract_first()
            pagerange = pagerange_scraped.strip()

        return pagerange

    def get_total_citations(self, response):
        total_citations = ""
        for total_citations_raw in response.xpath("//div[@class='tooltip__body']/div[@class='citation']/span"):
            total_citations_scraped = total_citations_raw.xpath("./text()").extract_first()
            total_citations = total_citations_scraped.strip()

        return total_citations

    def get_total_downloads(self, response):
        total_downloads = ""
        for total_downloads_raw in response.xpath("//div[@class='tooltip__body']/div[@class='metric']/span"):
            total_downloads_scraped = total_downloads_raw.xpath("./text()").extract_first()
            total_downloads = total_downloads_scraped.strip()

        return total_downloads

    def get_references(self, response):
        references = []
        for references_raw in response.xpath("//span[@class='references__note']"):
            current_reference = ""
            nodes = references_raw.xpath("./descendant::text()").getall()
            for n in nodes[0:-1]:
                current_reference += n
            
            if( current_reference not in references):
                references.append(current_reference )

        return references

    def get_doi(self, response):
        # Não está pegando certo!
        doi = ""
        for doi_raw in response.xpath("//div[@class='flex-container']"):
            description = doi_raw.xpath("./span[@class='bold']/text()").extract_first()
            content = doi_raw.xpath("./span[@class='space']/text()").extract_first()

            if( description is None):
                break
            elif( "DOI" in description ):
                doi = content.strip()

        return doi
    
    def get_isbn(self, response):
        # Pode dar problema!
        isbn = ""
        for isbn_raw in response.xpath("//div[@class='flex-container']"):
            description = isbn_raw.xpath("./span[@class='bold']/text()").extract_first()
            content = isbn_raw.xpath("./span[@class='space']/text()").extract_first()

            if( description is None):
                break
            elif( "ISBN" in description ):
                isbn = content.strip()

        return isbn

    ##############################################
    
    def export(self, article_authors, article_title, article_abstract, article_conference, article_date, article_ids, article_pagerange, article_doi, article_isbn, article_total_citations, article_total_downloads, article_references):
        filename = "Data/teste.data"
        f = open(filename, "a")

        print("Authors: ", end="", file=f)
        print(article_authors, file=f)
        print("Title: \"" + article_title + "\"", file=f)
        print("Abstract: \"" + article_abstract + "\"", file=f)
        print("Conference: \"" + article_conference + "\"", file=f)
        print("Date: \"" + article_date + "\"", file=f)
        print("IDS: \"" + article_ids + "\"", file=f)
        print("Page range: \"" + article_pagerange + "\"", file=f)
        print("DOI: \"" + article_doi + "\"", file=f)
        print("ISBN: \"" + article_isbn + "\"", file=f)
        print("Total Citations: \"" + article_total_citations + "\"", file=f)
        print("Total Downloads: \"" + article_total_downloads + "\"", file=f)
        print("References: ", file=f)
        for r in article_references:
            print(r, file=f)
        print("#----------------------#", file=f)

        f.close()


    ##############################################

    def parse(self, response):

        article_authors = self.get_authors(response)
        article_title = self.get_title(response)
        article_abstract = self.get_abstract(response)
        article_conference = self.get_conference(response)
        article_date = self.get_date(response)
        article_ids = self.get_ids(response)
        article_pagerange = self.get_pagerange(response)

        # Pode dar problema!
        article_doi = self.get_doi(response)
        article_isbn = self.get_isbn(response)

        ##############

        article_total_citations = self.get_total_citations(response)
        article_total_downloads = self.get_total_downloads(response)
        article_references = self.get_references(response)

        ##############
        print("=========================")
        print("Authors: ", end="")
        print(article_authors)
        print("Title: \"" + article_title + "\"")
        print("Abstract: \"" + article_abstract + "\"")
        print("Conference: \"" + article_conference + "\"")
        print("Date: \"" + article_date + "\"")
        print("IDS: \"" + article_ids + "\"")
        print("Page range: \"" + article_pagerange + "\"")
        print("DOI: \"" + article_doi + "\"")
        print("ISBN: \"" + article_isbn + "\"")
        print("Total Citations: \"" + article_total_citations + "\"")
        print("Total Downloads: \"" + article_total_downloads + "\"")
        print("=========================")
        # for r in article_references:
        #     print(">> " + r)
        print("Num referencias: " + str(len(article_references)))
        self.export(article_authors, article_title, article_abstract, article_conference, article_date, article_ids, article_pagerange, article_doi, article_isbn, article_total_citations, article_total_downloads, article_references)

