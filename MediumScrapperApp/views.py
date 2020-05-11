from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication   # noqa F401

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.db.models import Q


import json
import datetime
import logging
import time
import uuid
import sys
import threading

from MediumScrapperApp.models import *
from MediumScrapperApp.utils import *

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def HomePage(request):
    if request.user.is_authenticated():
    else:
        return HttpResponseRedirect("/login")



class LoginSubmitAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        response['message'] = "Error"

        try:

            data = request.data

            username = data['username']
            username = removeHtmlFromString(username)
            password = data['password']
            password = removeHtmlFromString(password)

            if len(User.objects.filter(username=username)) == 0:
                response['status'] = 301
                response['message'] = "No user found"
            else:
                try:
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    response['status'] = 200
                    response['message'] = "Success"
                except Exception as e:
                    response['status'] = 302
                    response['message'] = "Wrong password"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LoginSubmitAPI: %s at %s", e, str(exc_tb.tb_lineno))

        return Response(data=response)



LoginSubmit = LoginSubmitAPI.as_view()
