from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^home/$', views.HomePage), # Home Page
    url(r'^get-articles-based-on-query/$', views.GetArticlesBasedonQuery), # Search Articles API
    url(r'^get-next-n-articles/$', views.GetNextArticles), # Get Next N Articles API
    url(r'^article-page/$', views.GetArticlesPage), # Get Next N Articles API
]