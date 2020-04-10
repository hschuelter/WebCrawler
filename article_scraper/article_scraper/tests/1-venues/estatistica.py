def alfabetico(array):
    return array.sort()

def tirar_duplicadas(array):
    return list(dict.fromkeys(array))

def imprimir(array):
    for a in array:
        print(a)

def estatistica(array):
    filepath = 'BD-estatistica.txt'
    fp = open(filepath, 'w')

    d   = {}
    ret = {}
    for a in array:
        key = a.replace('https://', '').replace('http://', '').replace('www.', '')
        idx = key.find('/')
        key = key[:idx]
        if (not key in d):
            d[key] = 0
            ret[key] = []
        else:
            d[key] += 1
        
        ret[key].append(a)

    count = 0
    for key in d:
        count += d[key]

    sorting = []
    for key in d:
        sorting.append( (d[key], key) )
        # print(key, '->', d[key], '->', (1000*d[key]//count)/10, '%' ,file=fp)

    sorting.sort(reverse = True)
    for s in sorting:
        print(s[1], '->', s[0], '->', (1000*s[0]//count)/10, '%' ,file=fp)


    print('==============', file=fp)
    print('Total ->', count, file=fp)
    fp.close()

    return ret

def organiza(separado):
    file_prefixo = 'BD-links/'

    for key in separado:
        arquivo = file_prefixo + key.replace('.', '-') + '.links'
        fp = open(arquivo, 'w')

        for l in separado[key]:
            print(l, file=fp)

        fp.close()

def main():
    filepath = 'input/bd/BD-final.links'
    fp = open(filepath, 'r')
    links = fp.readlines()
    fp.close()

    links = list(map(lambda s : s.strip('\n'), links))
    alfabetico(links)
    # links = tirar_duplicadas(links)
    # imprimir(links)
    separado = estatistica(links)
    organiza(separado)



if __name__ == "__main__": main()