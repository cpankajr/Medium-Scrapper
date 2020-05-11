from django.db import models
from django.contrib import auth
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings

import sys
import json
import logging

from MediumScrapperApp.utils import *

class MediumSearchData(models.Model):

    user_query = models.TextField(default="")

    tag_data = models.TextField(default="[]")

    articles= models.ManyToManyField(
        'MediumArticle', blank=True)

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "MediumSearchData"
        verbose_name_plural = "MediumSearchDatas"

    def __str__(self):
        return self.user_query


class MediumArticle(models.Model):

    unique_id = models.TextField(default="")
    
    creator = models.CharField(default="", max_length=500)
    
    title = models.TextField(default="")
    
    date = models.DateField()
    
    read_time = models.IntegerField(default=0)
    
    details = models.TextField(default="")
    
    blog = models.TextField(default="")
    
    tags = models.ManyToManyField(
        'Tag', blank=True)

    class Meta:
        verbose_name = "MediumArticle"
        verbose_name_plural = "MediumArticles"

    def __str__(self):
        return self.title +" - " + self.unique_id

class Tag(models.Model):
    name = models.TextField(default="")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

        