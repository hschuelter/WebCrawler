import re
import json

def remove_tags(text):
    clean = re.compile('<.*?>')
    cleantext = re.sub(clean, '', text)
    return cleantext.strip('\n')

def to_dict(type_, title_, links_):
    d = {}
    d['type'] = type_
    d['title'] = []
    for t in title_:
        d['title'].append(remove_tags(t).lower())
    d['title'] = '; '.join(d['title'])

    d['links'] = []
    for l in links_:
        d['links'].append(remove_tags(l))

    return d

def get_data(fp, start, end):
    
    line = fp.readline()
    count = 0

    while (line):
        line = fp.readline()

        if (start in line):
            data = []
            while (not end in line):
                data.append(line.strip('\n'))
                line = fp.readline()
            data.append(line)

            # print_data(data)
            d = to_dict(
                start[1:],
                list(filter(lambda x: '<title>' in x, data)),
                list(filter(lambda x: ('<ee>' in x) or ('<url>' in x), data))
            )
            if ('interaction' in d['title']):
                # print_dict(d)
                print(json.dumps(d))
                # print('============')
            
def print_data(lista):
    for l in lista:
        print(l)

def print_dict(d):
    for key in d:
        print(key, '->', d[key])

def main():
    filepath = "less.xml"
    fp = open(filepath, 'r')
    
    # start = ['<article', '<inproceedings', '<proceedings', '<book', '<incollection', '<phdthesis', '<mastersthesis', '<www']
    # start = ['<article', '<inproceedings', '<proceedings', '<incollection']
    start = ['<proceedings']
    # end = ['</article', '</inproceedings', '</proceedings', '</book', '</incollection', '</phdthesis', '</mastersthesis', '</www']
    # end = ['</article', '</inproceedings', '</proceedings', '</incollection']
    end = ['</proceedings']
    
    for i in range(0, len(start)):
        fp.seek(0)
        get_data(fp, start[i], end[i])


if __name__ == "__main__":
    main()