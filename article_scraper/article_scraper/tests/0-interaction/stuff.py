def alfabetico(array):
    return array.sort()

def tirar_duplicadas(array):
    return list(dict.fromkeys(array))

def imprimir(array):
    for a in array:
        print(a)

def estatistica(array):
    filepath = 'estatistica.txt'
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

    for key in d:
        print(key, '->', d[key], '->', (1000*d[key]//count)/10, '%' ,file=fp)

    print('==============', file=fp)
    print('Total ->', count, file=fp)
    fp.close()

    return ret

def organiza(separado):
    file_prefixo = 'links/'

    for key in separado:
        arquivo = file_prefixo + key.replace('.', '-') + '.links'
        fp = open(arquivo, 'w')

        for l in separado[key]:
            print(l, file=fp)

        fp.close()

def main():
    filepath = 'final-artigos-less.links'
    fp = open(filepath, 'r')
    links = fp.readlines()
    fp.close()

    links = list(map(lambda s : s.strip('\n'), links))
    alfabetico(links)
    # links = tirar_duplicadas(links)
    imprimir(links)
    separado = estatistica(links)
    organiza(separado)



if __name__ == "__main__": main()