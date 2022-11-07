from bs4 import BeautifulSoup
import requests


source_url = 'https://theconversation.com/us/technology'
source_html = requests.get(source_url).text
soup = BeautifulSoup(source_html, 'lxml')
articles = soup.find_all('article')
for article in articles:
    if article.time:
        # print(article.time)
        pass
    article_header = article.find('div' , class_ = 'article--header')
    if article_header:
        link = article_header.a
        title = link.get_text()
        link = link.get('href')
        authors = []
        if article.p :
            for a in article.p.find_all('a'):
                authors.append(a.string)        
        print(title,*authors,link)
        print()
    summary = article.find('div', class_ = 'content')
    if summary:
        # print(summary.span.string)
        pass