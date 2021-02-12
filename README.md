# WebCrawler
Esse projeto contém diferentes Web Scrapers que realizam a coleta de metadados de artigos científicos nos sites da IEEE Xplore, ACM Digital Library e Springer Link.

Para executar algum scraper em específico, é necessário 
entrar na pasta `./article-scraper/article-scraper`.

O código de cada scraper está na pasta `./article-scraper/article-scraper/spiders`

## `scrapy crawl NOME_DO_SCRAPER`
Comando para iniciar a busca dos metadados.
O NOME_DO_SCRAPER pode ser substituído por:
    - acm
    - ieeex
    - springer_chapters 
    - springer_articles
dependendo do site desejado.
**Note: é necessário fornecer um conjunto de links para o scraper acessar, e alterar a variável `filepath` dentro do código do scraper.