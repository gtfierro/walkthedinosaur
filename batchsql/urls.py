from django.conf.urls import patterns, url

from batchsql import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^index$', views.index, name='index'),
        url(r'^define$', views.define_query, name='define'),
        url(r'^submit$', views.submit_query, name='submit'),
        url(r'^test$', views.test, name="test"),
        url(r'^submit-test$', views.submit_test, name='submit-test'),
        url(r'^status', views.status, name='status'),
        url(r'^downloads', views.downloads, name='downloads'),
        url(r'^database', views.database, name='database'),
)
