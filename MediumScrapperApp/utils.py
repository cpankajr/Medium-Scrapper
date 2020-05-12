from django.conf import settings
import re
import json
import logging
import requests
import sys
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
    article_divs = soup.findAll('div', class_="postArticle")
    articles = []
    for article_div in article_divs:
        article = {}
        article['title'] = article_div.findAll('div', class_="postArticle-content")[0].findAll('h3')[0].get_text()
        article['author'] = article_div.findAll('div', class_="postMetaInline-authorLockup")[0].findAll('a')[0].get_text()
        article_link = article_div.findAll('div', class_="postArticle-readMore")[0].a.get('href').split('?')[0].split('#')[0]
        article['link'] = article_link
        article['date'] = article_div.findAll('time')[0].get_text()
        article['datetime'] = article_div.findAll('time')[0].get('datetime')
        article['reading_time'] = article_div.findAll('span', class_="readingTime")[0].get('title').split()[0]
        content , tags = get_article_html(article_link)
        article ['unique-id'] = article_link.split("-")[-1]
        article ['tags'] = tags
        articles.append(article)
    return articles

def get_article_html(url):
    try:
        content = ''
        tags = []
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        if soup.find('article'):
            for i in soup.select('article'):
                content += i.get_text()
        metadata  = json.loads(str(soup.findAll('script',{"type":"application/ld+json"})[0].decode_contents()))
        tags = [x.replace("Tag:","").lower() for x in metadata["keywords"] if "Tag:" in x]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.info("Error while scrapping url: "+ str(url) +" ---- "+str(e)+" ---- " + str(exc_tb.tb_lineno))
    return content , tags
    