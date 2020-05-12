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
                article_data = json.loads(MediumSearchData.objects.get(user_query=user_query.lower()).search_data)
            except ObjectDoesNotExist:
                articles_data = get_articles_based_on_query(user_query.lower())
                search_obj = MediumSearchData.objects.create(user_query=user_query.lower(),search_data=json.dumps(articles_data))
                save_article_details_in_db.delay(articles_data,search_obj.pk)

            response['status'] = 200
            response['articles_data'] = articles_data
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
            contents,tags = get_article_html(article['link'])
            articles_objs.append(MediumArticle.objects.create(unique_id=article ['unique-id'],
                                                    creator=article["author"],
                                                    title=article["title"],
                                                    read_time = article['reading_time'],
                                                    blog = contents,
                                                    tags = tags))
    for articles_obj in articles_objs:
        search_obj.articles.add(articles_obj)
        search_obj.save()
            

