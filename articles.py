from bs4 import BeautifulSoup
import requests
import json
import time
import concurrent.futures

source_base = 'https://theconversation.com/'

test_article_url = 'https://theconversation.com/humans-are-8-virus-how-the-ancient-viral-dna-in-your-genome-plays-a-role-in-human-disease-and-development-192322'

def get_article_content(article_url):
    article_page = requests.get(article_url).text
    article_soup = BeautifulSoup(article_page, 'lxml')
    body = article_soup.find('div', itemprop='articleBody')
    return body.get_text(strip=True)

def create_article_dict(article):
    """
        Takes an article tag on https://theconversation.com/ and return the corresponding python dictionnary
    """
    article_dict = {
        'title' : '',
        'image' : '',
        'summary' : '',
        'content' : '',
        'authors' : [],
        'published' : None
    }

    image = article.find('img', class_='lazyload')
    if image:
        image_url = image.get('data-src')
        article_dict['image'] = image_url

    if article.time:
        article_dict['published'] = article.time.get('datetime')

    article_header = article.find('div' , class_ = 'article--header')
    if article_header:
        link = article_header.a
        title = link.get_text()
        article_dict['title'] = title

        relative_link = link.get('href')
        full_link = source_base + str(relative_link).strip()
        article_dict['content'] = get_article_content(article_url=full_link)

        authors = []
        if article.p :
            for a in article.p.find_all('a'):
                authors.append(a.get_text())
        article_dict['authors'] = authors 
    
    summary = article.find('div', class_ = 'content')
    if summary:
        article_dict['summary'] = summary.span.get_text()

    return article_dict


source_main_page_url = 'https://theconversation.com/us/technology'
source_html = requests.get(source_main_page_url).text
soup = BeautifulSoup(source_html, 'lxml')
articles_dict = {}
articles = soup.find_all('article')

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [executor.submit(create_article_dict,article) for article in articles]

    for count,completed in enumerate(concurrent.futures.as_completed(results)):
        articles_dict[count] = completed.result()
        
# for article in articles_dict:
#     if not articles_dict[article]['image']:
#         print(articles_dict[article])
#         break
articles_json = json.dumps(articles_dict, indent = 4)
# print(articles_json)