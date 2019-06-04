from requests_html import HTMLSession
from meta import Meta

def create_queue_file(session, base_url):
    links = set()
    req = session.get(base_url)

    for l in req.html.links:
        if ("https://doi.org/" in l or "dl.acm.org/" in l):
            links.add(l)

    print( "Numero de links: " + str(len(links)) )
    f = open("./queue.links", 'w')
    for l in links:
            f.write(l + '\n')
    f.close()

def all_ihc_links(session, base_url):
    links = set()
    req = session.get("https://dblp.uni-trier.de/db/conf/ihc/")

    for l in req.html.links:
        if "https://dblp.uni-trier.de/db/conf/ihc/ihc" in l:
            links.add(l)

    f = open("./all-ihc.links", 'w')
    for l in links:
        f.write(l + '\n')
    f.close()

    return links

def main():
    base_url = "https://dblp.uni-trier.de/db/conf/ihc/"
    session = HTMLSession()

    all_links = all_ihc_links(session, base_url)
    for link in all_links:
        print("Verificando <" + link + ">...")
        create_queue_file(session, link)

        file_path = "./Data/" + link[38:46]
        if( file_path[len(file_path) - 1] == '.' ):
            file_path += "txt"
        else:
            file_path += ".txt"

        fp = open(file_path, 'w')
        fp.close()

        f = open("./queue.links", 'r')
        while True:
            next_link = f.readline()
            if next_link == '':
                break

            req = session.get(next_link)
            meta = Meta()
            meta.feed( req.html.find('meta') )
            meta.parse_meta_data()
            # meta.show_meta_data()
            meta.print_meta_data(file_path)
        
        print("OK")
    # f.close()

if __name__ == "__main__": main()