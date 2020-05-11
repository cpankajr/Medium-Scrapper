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
    return render(request,"MediumScrapperApp/home.html")