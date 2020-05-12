from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication   # noqa F401

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect

import json
import datetime
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
                articles_data = get_articles_based_on_query(user_query=user_query.lower())
                search_obj = MediumSearchData.objects.create(user_query=user_query.lower(),search_data=json.dumps(articles_data))
                save_article_details_in_db.delay(articles_data,search_obj)
            response['status'] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetArticlesBasedonQuery: %s at %s",
                         str(e), str(exc_tb.tb_lineno))

        return Response(data=response)

GetArticlesBasedonQuery = GetArticlesBasedonQueryAPI.as_view()

@shared_task
def save_article_details_in_db(articles_data,search_obj):
    for article in articles_data:
        contents,tag = get_article_html(article['link'])
