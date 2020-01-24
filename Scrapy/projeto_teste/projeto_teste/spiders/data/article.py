class Article:
    authors = []
    title = ""
    abstract = ""
    date = ""
    pages = ""
    doi = ""
    keywords = []
    references = []

    def __init__(self, authors, title, abstract, date, pages, doi, keywords, references):
        self.authors = authors
        self.title = title
        self.abstract = abstract
        self.date = date
        self.pages = pages
        self.doi = doi
        self.keywords = keywords
        self.references = references

    def __init__(self):
        self.authors = []
        self.title = ""
        self.abstract = ""
        self.date = ""
        self.pages = ""
        self.doi = ""
        self.keywords = ""
        self.references = ""