from django.conf.urls import patterns, include, url

from batchsql.views import index

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'walkthedinosaur.views.home', name='home'),
    url(r'^/?$', index),
    url(r'^batchsql/', include('batchsql.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Sentry
    # (r'^sentry/', include('sentry.web.urls')),
)
