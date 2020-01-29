# scrapy crawl acm -o Data/teste.json > a.txt
import scrapy
import requests

# from .data.article import Article
from .data.author  import Author

class ACM_Spider(scrapy.Spider):
    name = "acm"

    test_urls_1 = [
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

    test_urls_2 = [
        # Data mining
        "https://dl.acm.org/doi/abs/10.1145/502512.502517"  ,
        "https://dl.acm.org/doi/abs/10.1145/545151.545180"  ,
        "https://dl.acm.org/doi/abs/10.5555/1074100.1074308",
        "https://dl.acm.org/doi/abs/10.1145/233269.280351"  ,
        "https://dl.acm.org/doi/abs/10.1145/1288552.1288559",
        # Metaheuristics
        "https://dl.acm.org/doi/abs/10.1145/937503.937505"  ,
        "https://dl.acm.org/doi/abs/10.1145/1276958.1277303",
        "https://dl.acm.org/doi/abs/10.1145/3090354.3090462",
        "https://dl.acm.org/doi/abs/10.1145/1143997.1144172",
        "https://dl.acm.org/doi/abs/10.5555/2665008.2665011",
        # Gamification
        "https://dl.acm.org/doi/abs/10.1145/2583008.2583029",
        "https://dl.acm.org/doi/abs/10.1145/3012430.3012600",
        "https://dl.acm.org/doi/abs/10.5555/2685617.2685674",
        "https://dl.acm.org/doi/abs/10.1145/2669711.2669895",
        "https://dl.acm.org/doi/abs/10.1145/3121113.3121205"
     ]
    start_urls = test_urls_2

    # start_urls = [
    #     "https://dl.acm.org/doi/10.1145/3357155.3358455", # "A proposal to ..." (IHC 2019)
    #  ]


    def extract_authors(self, response): #***********************
        authors = []
        authors_names = []
        for author_names_raw in response.xpath("//a[@class='author-name']"):
            name = author_names_raw.xpath("./@title").extract_first()

            institute = author_names_raw.xpath("./span/span[@class='loa_author_inst']/p/text()").extract_first()
            if( institute is None):
                institute = ""

            # print(institute)

            if ( name not in authors_names):
                new_author = Author(name, institute)
                authors.append(new_author)

                authors_names.append(name)
        
        return authors

    def extract_title(self, response):
        xpath_string = "//h1[@class='citation__title']/text()"
        title = response.xpath(xpath_string).getall()
        title = ''.join(title)

        return str(title)

    def extract_abstract(self, response):
        xpath_string = "//div[@class='article__section article__abstract hlFld-Abstract']/p/descendant::text()"
        abstract = response.xpath(xpath_string).getall()

        if( len(abstract) == 0):
            xpath_string = "//div[@class='abstractSection abstractInFull']/p/descendant::text()"
            abstract = response.xpath(xpath_string).getall()

        if( len(abstract) > 0 ):
            abstract = ''.join(abstract)
            return str(abstract)
        
        return ""

    # # Posso utilizar no futuro
    # def extract_conference(self, response): #***********************
    #     conference = ""
    #     for conference_raw in response.xpath("//span[@class='epub-section__title']"):
    #         conference_scraped = conference_raw.xpath("./text()").extract_first()
    #         conference = conference_scraped.strip()

    #     return str(conference)

    def extract_date(self, response): #***********************
        date = ""
        for dates_raw in response.xpath("//span[@class='epub-section__date']"):
            date_scraped = dates_raw.xpath("./text()").extract_first()
            date = date_scraped.strip()

        return str(date)

    def extract_pages(self, response): #***********************
        pages = ""
        for pages_raw in response.xpath("//span[@class='epub-section__pagerange']"):
            pages_scraped = pages_raw.xpath("./text()").extract_first()
            pages = pages_scraped.strip()

        if( pages != ""):
            pages = pages.replace('Pages', '')
            pages = pages.replace(' ', '')
            dash = ""
            for ch in pages:
                if(not ch.isdigit()):
                    dash = ch

            if(dash != ""):
                pages = pages.split(dash)
                pages = int(pages[1]) - int(pages[0]) + 1

        return str(pages)

    def extract_references(self, response): #***********************
        references = []
        for references_raw in response.xpath("//span[@class='references__note']"):
            current_reference = ""
            nodes = references_raw.xpath("./descendant::text()").getall()
            for n in nodes[0:-1]:
                current_reference += n
            
            if( current_reference not in references):
                references.append(current_reference )

        return references

    def extract_doi(self, response):
        xpath_string = "//input[@name='doiVal']/@value"
        doi = response.xpath(xpath_string).get()

        return str(doi)

    def extract_publication(self, response):
        xpath_string = "//div[@class='issue-item__detail']/a/@href"
        url = response.xpath(xpath_string).get()
        url = response.urljoin(url)

        publication = dict()
        new_response = requests.get(url)
        code = new_response.text.split('\n')

        title = ""
        publisher = ""
        conference = ""
        code = list( filter(lambda a: a != '', code) )
        
        for i in range(0, len(code)-1):
            if( "Publisher:" in code[i]):
                publisher = code[i].split('<ul class="rlist--inline comma">')[1]
                publisher = publisher.split('</ul>')[0]
                publisher = self.remove_tags(publisher)
                publisher = publisher.replace("Publisher:", "")


                conference = ""
                conference = self.remove_tags( code[i] )
                conference = conference.replace("Publisher:", "")
                aux = conference.split("Conference:")

                if(len(aux) == 1):
                    conference = ""

                if(len(aux) > 1):
                    conference = self.remove_tags( aux[1] )
                    conference = conference.strip(' ')

                # print( "Publisher  - " + publisher )
                # print( "Conference - " + conference )


            if( "<title>" in code[i] ):
                title = self.remove_tags( code[i] )
                title = title.split( ' | ' )[0]

        publication['title'] = title
        publication['publisher'] = publisher
        publication['conference'] = conference
        publication['url'] = url
        print( "**************************************************" )
        print( publication )
        print( "**************************************************" )

        return publication

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
    
    def export(self, article, authors):
        filename = "Data/acm.data"
        f = open(filename, "a")
        print("\nAuthors: ", file=f)
        for a in authors:
            print('\t' + str(a), file=f)
        print("\nTitle: \"" + article['title'] + "\"", file=f)
        print("\nAbstract: \"", file=f, end="")
        print(article['abstract'], file=f, end="\"\n")
        print("\nDate: \"" + article['date'] + "\"", file=f)
        print("\nPages: \"" + article['pages'] + "\"", file=f)
        print("\nDOI: \"" + article['doi'] + "\"", file=f)
        print("\nReferences: ", file=f)
        for i in range(0, len(article['references']) ):
            print(str(i) + ". " + article['references'][i],  file=f)
            print("", file=f)
        print("=========================", file=f)

        f.close()


    ##############################################

    def parse(self, response):

        authors = []
        article = dict()
        publication = dict()

        authors = self.extract_authors(response)

        ################
        article['authors'] = []
        for a in authors:
            article['authors'].append(a.name)

        article['title'] = self.extract_title(response)
        article['abstract'] = self.extract_abstract(response)
        article['date'] = self.extract_date(response)
        article['pages'] = self.extract_pages(response)
        article['doi'] = self.extract_doi(response)
        # article['keywords'] = article_keywords
        article['references'] = self.extract_references(response)

        publication = self.extract_publication(response)

        self.export(article, authors)

