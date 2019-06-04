
class Meta:
    raw_meta = []

    def __init__(self):
        self.publisher = ""
        self.conference = ""
        self.title = ""
        self.date = ""
        self.isbn = ""
        self.authors = []
        self.keywords = []

    def feed(self, raw_meta):
        for m in raw_meta:
            m_string = str(m)
            self.raw_meta.append(m_string)

        # for s in self.raw_meta:
        #     print(s)
    
    def parse_meta_data(self):
        for m in self.raw_meta:
            start_position = m.find("=") + 2
            end_position = m.find(" name") - 1

            if "citation_publisher" in m:
                self.publisher = m[start_position:end_position]

            elif "citation_conference" in m:
                self.conference = m[start_position:end_position]

            elif "citation_title" in m:
                self.title = m[start_position:end_position]

            elif "citation_date" in m:
                self.date = m[start_position:end_position]

            elif "citation_isbn" in m:
                self.isbn = m[start_position:end_position]

            elif "citation_authors" in m:
                self.authors = slice_string(m[start_position:end_position])

            elif "citation_keywords" in m:
                self.keywords = slice_string(m[start_position:end_position])

        # self.show_meta_data()

    def show_meta_data(self):
        print("Publisher: " + self.publisher)
        print("Conference: " + self.conference)
        print("Title: " + self.title)
        print("Date: " + self.date)
        print("ISBN: " + self.isbn)
        print("Authors: ", end="")
        print( '; '.join(map(str, self.authors)) )
        print("Keywords: ", end="")
        print( '; '.join(map(str, self.keywords)) )

    def print_meta_data(self, file_path):
        fp = open(file_path, 'a')
        fp.write("Publisher: " + self.publisher + '\n')
        fp.write("Conference: " + self.conference + '\n')
        fp.write("Title: " + self.title + '\n')
        fp.write("Date: " + self.date + '\n')
        fp.write("ISBN: " + self.isbn + '\n')
        fp.write("Authors: ")
        fp.write( '; '.join(map(str, self.authors))  + '\n')
        fp.write("Keywords: ")
        fp.write( '; '.join(map(str, self.keywords))  + '\n')
        fp.write("\n####################################\n\n")

        fp.close()


def slice_string(raw_string):
    array = []
    
    pos = raw_string.find(";")
    while(pos != -1):
        array.append(raw_string[0:pos])
        raw_string = raw_string[pos+2:]
        pos = raw_string.find(";")

    array.append(raw_string)
    return array
