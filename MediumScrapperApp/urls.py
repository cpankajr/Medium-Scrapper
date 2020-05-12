from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^home/$', views.HomePage), # Home Page
    url(r'^get-articles-based-on-query/$', views.GetArticlesBasedonQuery), # Search Articles API
]