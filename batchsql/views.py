from django.http import HttpResponse, HttpResponseRedirect 
from django.core.urlresolvers import reverse
from django.shortcuts import render

from batchsql.models import QueuedJob, CompletedJob, TestQuery
import connection
from datetime import date
tables = connection.tables
patent_types = connection.patent_types
years = [i for i in range (1980, date.today().year + 1)]
months = [i for i in range (1,13)]
days = [i for i in range (1,32)]

def index(request):
    number_of_queries = len(QueuedJob.objects.all())
    number_of_finished = len(CompletedJob.objects.all())
    context = {'number_of_queries': number_of_queries,
               'jobs': QueuedJob.objects.all(),
               'number_of_finished': number_of_finished}
    return render(request, 'batchsql/index.html', context)

def define_query(request):
    context = {'tables': tables}
    return render(request, 'batchsql/define.html', context)

def submit_query(request):
    querystring = request.POST.get('querystring')
    tablename = request.POST.get('tablename')
    fields = request.POST.getlist('fields')
    email = request.POST.get('email')
    requested_format = request.POST.get('dataformat')
    job = QueuedJob.create(tablename, fields, requested_format, email, querystring)
    job.save()
    return HttpResponseRedirect('index')

def test(request):
    context = {'tables': tables, 'patent_types': patent_types, 'months':months, 'years':years, 'days':days}
    return render(request, 'batchsql/test.html', context)

def submit_test(request):
    newQuery = TestQuery(request.POST)
    querystring = newQuery.getQueryString()
    email = request.POST.get('email')
    requested_format = request.POST.get('dataformat')
    job = QueuedJob.create(None, None, requested_format, email, querystring)
    job.save()
    return HttpResponseRedirect('index')