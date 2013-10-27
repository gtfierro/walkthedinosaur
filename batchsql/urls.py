from django.conf.urls import patterns, url

from batchsql import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^index$', views.index, name='index'),
        url(r'^define$', views.define_query, name='define'),
        url(r'^submit$', views.submit_query, name='submit'),
        url(r'^test$', views.test, name="test"),
        url(r'^submit-test$', views.submit_test, name='submit-test'),
)
