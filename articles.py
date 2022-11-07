from bs4 import BeautifulSoup
import requests
import json

source_base = 'https://theconversation.com/us'

source_article_url = 'https://theconversation.com/humans-are-8-virus-how-the-ancient-viral-dna-in-your-genome-plays-a-role-in-human-disease-and-development-192322'

def get_article_content(article_url):
    article_page = requests.get(article_url).text
    article_soup = BeautifulSoup(article_page, 'lxml')
    body = article_soup.find('div', itemprop = 'articleBody')
    return body.get_text().strip()


source_main_page_url = 'https://theconversation.com/us/technology'
source_html = requests.get(source_main_page_url).text
soup = BeautifulSoup(source_html, 'lxml')
articles_dict = {}
articles = soup.find_all('article')
for count,article in enumerate(articles):
    articles_dict[count] = {
        'title' : '',
        'summary' : '',
        'content' : '',
        'authors' : [],
        'published' : None
    }

    if article.time:
        articles_dict[count]['published'] = article.time.get('datetime')
    article_header = article.find('div' , class_ = 'article--header')
    if article_header:
        link = article_header.a
        title = link.get_text()
        articles_dict[count]['title'] = title

        relative_link = link.get('href')
        # content = body.get_text()
        # articles_dict[count]['content'] = content

        authors = []
        if article.p :
            for a in article.p.find_all('a'):
                authors.append(a.get_text())
        articles_dict[count]['authors'] = authors 
    summary = article.find('div', class_ = 'content')
    if summary:
        articles_dict[count]['summary'] = summary.span.get_text()

articles_json = json.dumps(articles_dict, indent = 4)
# print(articles_json)