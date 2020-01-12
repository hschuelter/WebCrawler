import scrapy

class IHCSpider(scrapy.Spider):
    name = "ihc"
    start_urls = [
        "https://dblp.uni-trier.de/db/conf/ihc/"
    ]

    def parse(self, response):
        print("=========================")
        for link in response.xpath("//li[not(@id) and not(@class)]"):
            link_text = link.xpath(".//a/@href").extract_first()

            if( link_text is not None ):
                print(">>> " + link_text)
                yield {
                    'link-url': link.xpath(".//a/@href").extract_first()
                }

        print("=========================")