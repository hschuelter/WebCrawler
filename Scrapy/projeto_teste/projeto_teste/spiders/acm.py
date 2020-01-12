import scrapy

class ACM_Spider(scrapy.Spider):
    name = "acm"
    start_urls = [
        "https://dl.acm.org/doi/10.1145/3357155.3358455"
    ]
    # "https://dl.acm.org/doi/10.1145/3357155.3358455" -> "A proposal to adapt..."  (IHC 2019)
    # "https://dl.acm.org/doi/10.1145/3160504.3160512" -> "A Systematic Mapping..." (IHC 2017) 


    def parse(self, response):
        article_authors = []
        article_title = ""
        article_abstract = ""
        article_conference = ""
        article_date = ""
        article_ids = ""
        article_pagerange = ""
        article_doi = ""
        article_isbn = ""

        # 
        article_total_citations = ""
        article_total_downloads = ""
        article_references = []
        
        for author_names_raw in response.xpath("//a[@class='author-name']"):
            author_name = author_names_raw.xpath("./@title").extract_first()

            if (author_name not in article_authors):
                article_authors.append(author_name)


        for titles_raw in response.xpath("//h1[@class='citation__title']"):
            title_scraped = titles_raw.xpath("./text()").extract_first()
            article_title = title_scraped.strip()

        for abstract_raw in response.xpath("//div[@class='article__section article__abstract hlFld-Abstract']/p"):
            abstract_scraped = abstract_raw.xpath("./text()").extract_first()
            article_abstract = abstract_scraped.strip()

        for conference_raw in response.xpath("//span[@class='epub-section__title']"):
            conference_scraped = conference_raw.xpath("./text()").extract_first()
            article_conference = conference_scraped.strip()
        
        for dates_raw in response.xpath("//span[@class='epub-section__date']"):
            date_scraped = dates_raw.xpath("./text()").extract_first()
            article_date = date_scraped.strip()

        for ids_raw in response.xpath("//span[@class='epub-section__ids']"):
            ids_scraped = ids_raw.xpath("./text()").extract_first()
            article_ids = ids_scraped.strip()

        for pagerange_raw in response.xpath("//span[@class='epub-section__pagerange']"):
            pagerange_scraped = pagerange_raw.xpath("./text()").extract_first()
            article_pagerange = pagerange_scraped.strip()

        # Pode dar problema!
        for isbn_doi_raw in response.xpath("//div[@class='flex-container']"):
            description = isbn_doi_raw.xpath("./span[@class='bold']/text()").extract_first()
            content = isbn_doi_raw.xpath("./span[@class='space']/text()").extract_first()

            if( description is None):
                break
            elif( "ISBN" in description ):
                article_isbn = content.strip()
            elif( "DOI" in description ):
                article_doi = content.strip()

        ##############

        for total_citations_raw in response.xpath("//div[@class='tooltip__body']/div[@class='citation']/span"):
            total_citations_scraped = total_citations_raw.xpath("./text()").extract_first()
            article_total_citations = total_citations_scraped.strip()

        for total_downloads_raw in response.xpath("//div[@class='tooltip__body']/div[@class='metric']/span"):
            total_downloads_scraped = total_downloads_raw.xpath("./text()").extract_first()
            article_total_downloads = total_downloads_scraped.strip()

        for references_raw in response.xpath("//span[@class='references__note']"):
            reference = ""
            nodes = references_raw.xpath("./descendant::text()").getall()
            for n in nodes[0:-1]:
                reference += n
            
            if( reference not in article_references):
                article_references.append(reference)

            # if( au is not None ):
            #     print(">>> " + au)
                # yield {
                #     'link-url': link.xpath(".//a/@href").extract_first()
                # }

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