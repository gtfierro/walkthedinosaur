from django.conf.urls import patterns, url

from batchsql import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^define$', views.define_query, name='define'),
)