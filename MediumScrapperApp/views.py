from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication   # noqa F401
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect

import json
import logging
import time
import uuid
import sys
import threading

from MediumScrapperApp.models import *
from MediumScrapperApp.utils import *
from celery import shared_task

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def HomePage(request):
    return render(request,"MediumScrapperApp/home.html")

class GetArticlesBasedonQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            user_query = data['user_query']
            articles_data=[]
            try:
                search_obj = MediumSearchData.objects.get(user_query=user_query.lower())
                articles_data = json.loads(search_obj.search_data)[:10]
                no_of_results = search_obj.no_of_results
            except ObjectDoesNotExist:
                articles_data, response_json_data, no_of_results = get_articles_list_based_on_query(user_query.lower())
                search_obj = MediumSearchData.objects.create(user_query=user_query.lower(),
                                                            search_data=json.dumps(articles_data),
                                                            no_of_results=int(no_of_results),
                                                            raw_json_data=json.dumps(response_json_data),)
                search_obj_pk = search_obj.pk
                save_article_details_in_db.delay(articles_data,search_obj_pk)

            if len(articles_data) == 0:
                tags = get_tag_suggestion(user_query)
                response['status'] = 301
                response['suggested_tags'] = tags
            else:
                response['status'] = 200
                response['articles_data'] = articles_data
                response['no_of_results'] = no_of_results
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetArticlesBasedonQuery: %s at %s",
                         str(e), str(exc_tb.tb_lineno))

        return Response(data=response)

GetArticlesBasedonQuery = GetArticlesBasedonQueryAPI.as_view()

@shared_task
def save_article_details_in_db(articles_data,search_obj_pk):
    search_obj = MediumSearchData.objects.get(pk=search_obj_pk)
    articles_objs = []
    for article in articles_data:
        try:
            articles_objs.append(MediumArticle.objects.get(unique_id=article ['unique-id']))
        except ObjectDoesNotExist:
            contents, tags, comments = get_article_page_data(article['link'])
            articles_objs.append(MediumArticle.objects.create(unique_id=article ['unique-id'],
                                                    creator=article["author"],
                                                    title=article["title"],
                                                    read_time = article['reading_time'],
                                                    blog = contents,
                                                    tags = json.dumps(tags),
                                                    comments = json.dumps(comments)
                                                    )
                                                )
    for articles_obj in articles_objs:
        search_obj.articles.add(articles_obj)
        search_obj.save()
            

class GetNextArticlesAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            user_query = data['user_query']
            start = int(data['start'])
            limit = int(data['limit'])
            articles_data=[]    
            search_obj = MediumSearchData.objects.get(user_query=user_query.lower())
            no_of_results = search_obj.no_of_results
            if no_of_results>= (start+limit):
                response_json_data = json.loads(search_obj.raw_json_data)
                articles_data = get_next_n_articles(start,limit,response_json_data)
                search_obj.search_data = json.dumps(json.loads(search_obj.search_data)+articles_data)
                search_obj.save()
                search_obj_pk = search_obj.pk
                save_article_details_in_db.delay(articles_data,search_obj_pk)
                response['status'] = 200
                response['articles_data'] = articles_data
                response['no_of_results'] = search_obj.no_of_results
            else:
                response['status'] = 301
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetNextArticlesAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno))

        return Response(data=response)

GetNextArticles = GetNextArticlesAPI.as_view()