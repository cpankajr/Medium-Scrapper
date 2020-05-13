from django.conf import settings
import re
import json
import logging
import requests
import sys
from bs4 import BeautifulSoup
import datetime
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
    tags = []
    if len(main_tags_div)>0:
        tag_divs = main_tags_div[0].find_all("li")
        for tag_div in tag_divs:
            tags.append(tag_div.getText())
    return tags

def get_articles_based_on_query(query):
    html = get_html('https://medium.com/tag/'+str(query)+"/latest")
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
        article ['unique-id'] = article_link.split("-")[-1]
        articles.append(article)
    return articles



def get_article_page_data(url):
    try:
        content = ''
        tags = []
        comments = []
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        if soup.find('article'):
            for i in soup.select('article'):
                content += i.get_text()
        metadata  = json.loads(str(soup.findAll('script',{"type":"application/ld+json"})[0].decode_contents()))
        tags = [x.replace("Tag:","").lower() for x in metadata["keywords"] if "Tag:" in x]

        article_unique_id = url.split("/")[-1]
        
        html = get_html("https://medium.com/_/api/posts/"+article_unique_id+"/responsesStream")
        response_json_data = json.loads(html.decode().replace("])}while(1);</x>",""))
        stream_items = response_json_data["payload"]["streamItems"]
        for stream_item in stream_items:
            response_id = stream_item["postPreview"]["postId"]
            response_user_id = response_json_data["payload"]["references"]["Post"][str(response_id)]["creatorId"]
            html = get_html("https://medium.com/"+str(response_user_id)+"/"+str(response_id))
            soup = BeautifulSoup(html, 'html.parser')
            comment = {}
            comment ["text"] = soup.find('article').findAll("section")[2].get_text()
            comment ["user"] = soup.find('article').findAll("section")[1].findAll('a')[1].get_text()
            comments.append(comment)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.info("Error get_article_page_data url: "+ str(url) +" ERROR: "+str(e)+" at line no: " + str(exc_tb.tb_lineno))
    return content , tags,comments

def get_articles_list_based_on_query(query):
    articles = []
    response_json_data = {}
    no_of_results = 0
    try:
        query = query.replace(" ","-")
        time_stamp = int(datetime.datetime.now().timestamp()*1000)
        # print("https://medium.com/_/api/tags/"+str(query)+"/stream?limit=100&to="+str(time_stamp)+"&sortBy=published-at")
        html = get_html("https://medium.com/_/api/tags/"+str(query)+"/stream?limit=100&to="+str(time_stamp)+"&sortBy=published-at")
        response_json_data = json.loads(html.decode().replace("])}while(1);</x>",""))
        stream_items = response_json_data["payload"]["streamItems"]
        no_of_results = len(stream_items)
        for stream_item in stream_items[:10]:
            article = {}
            article_unique_id = stream_item["postPreview"]["postId"]
            author_id = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["creatorId"]
            author_name = response_json_data["payload"]["references"]["User"][str(author_id)]["name"]
            article_title = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["title"]
            article_date = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["createdAt"]
            reading_time = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["virtuals"]["readingTime"]
            claps = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["virtuals"]["totalClapCount"]
            article_link = "https://medium.com/"+str(author_id)+"/"+str(article_unique_id)

            article['title'] = article_title
            article['author'] = author_name
            article['link'] = article_link
            article['datetime'] = article_date
            article['date'] = datetime.datetime.utcfromtimestamp(article_date/1000.0).strftime('%-d %b %Y')
            article['reading_time'] = reading_time
            article ['unique-id'] = article_unique_id
            article ['claps'] = claps
            articles.append(article)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.info("Error get_articles_list_based_on_query: "+str(e)+" at line no: " + str(exc_tb.tb_lineno))
    return articles,response_json_data,no_of_results

def get_next_n_articles(start,n,response_json_data):
    articles = []
    try:
        stream_items = response_json_data["payload"]["streamItems"] 
        for stream_item in stream_items[start:start+n]:
            article = {}
            article_unique_id = stream_item["postPreview"]["postId"]
            author_id = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["creatorId"]
            author_name = response_json_data["payload"]["references"]["User"][str(author_id)]["name"]
            article_title = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["title"]
            article_date = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["createdAt"]
            reading_time = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["virtuals"]["readingTime"]
            claps = response_json_data["payload"]["references"]["Post"][str(article_unique_id)]["virtuals"]["totalClapCount"]
            article_link = "https://medium.com/"+str(author_id)+"/"+str(article_unique_id)

            article['title'] = article_title
            article['author'] = author_name
            article['link'] = article_link
            article['datetime'] = article_date
            article['date'] = datetime.datetime.utcfromtimestamp(article_date/1000.0).strftime('%-d %b %Y')
            article['reading_time'] = reading_time
            article ['unique-id'] = article_unique_id
            article ['claps'] = claps
            articles.append(article)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.info("Error get_next_n_articles: "+str(e)+" at line no: " + str(exc_tb.tb_lineno))

    return articles