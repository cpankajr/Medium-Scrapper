from django.conf import settings
import re
import json
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def remove_html_from_string(raw_str):
    regex_cleaner = re.compile('<.*?>')
    cleaned_raw_str = re.sub(regex_cleaner, '', raw_str)
    return cleaned_raw_str

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    r = requests.get(url=url, headers=headers)
    content = r.content
    return content

def get_tag_suggestion(query):
    html = get_html('https://medium.com/search/tags?q='+str(query))
    soup = BeautifulSoup(html, 'html.parser')
    main_tags_div = soup.find_all("ul", class_="tags tags--postTags tags--light")
    if len(main_tags_div)>0:
        tag_divs = main_tags_div[0].find_all("li")
        for tag_div in tag_divs:
            print(tag_div.getText())

def get_articles_based_on_query(query):
    html = get_html('https://medium.com/tag/'+str(query))
    links = []
    soup = BeautifulSoup(html, 'html.parser')
    article_links = soup.findAll('div', class_="postArticle-readMore")
    articles = []
    for link in article_links:
        articles.append(get_article_data(link.a.get('href').split('?')[0].split('#')[0]))
    return articles

def get_article_data(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    content = ''
    article = {}
    title = soup.findAll('title')[0]
    article['title'] = title.get_text()
    author = soup.findAll('meta', {"name": "author"})[0]
    article['author'] = author.get('content')
    article['link'] = url
    reading_time = int(soup.findAll('meta', {"name":"twitter:data1"})[0].get('value').split()[0])
    article['reading_time'] = reading_time

    if soup.find('article'):
        for i in soup.select('article'):
            content += i.getText()
        # article["content"] = content
    else:
        return {}
    return article
