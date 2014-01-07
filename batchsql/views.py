from django.http import HttpResponse, HttpResponseRedirect 
from django.core.urlresolvers import reverse
from django.shortcuts import render
from tasks import dojob

from batchsql.models import QueuedJob, CompletedJob, TestQuery
import connection
from datetime import date
tables = connection.tables
years = [i for i in range (1980, date.today().year + 1)]
months = [i for i in range (1,13)]
days = [i for i in range (1,32)]
years.insert(0, '')
months.insert(0, '')
days.insert(0, '')


def index(request):
    context = {'page': 'home'}
    return render(request, 'batchsql/index.html', context)

def status(request):
    number_of_queries = len(QueuedJob.objects.all())
    number_of_finished = len(CompletedJob.objects.all())
    context = {'number_of_queries': number_of_queries,
               'jobs': QueuedJob.objects.all(),
               'number_of_finished': number_of_finished,
               'page': 'status'}
    return render(request, 'batchsql/status.html', context)


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
    return HttpResponseRedirect('status')

def test(request):
    context = {'tables': tables, 'months':months, 'years':years, 'days':days, 
               'page': 'query'}
    return render(request, 'batchsql/test.html', context)

def submit_test(request):
    newQuery = TestQuery(request.POST)
    querystring = newQuery.getQueryString()
    email = request.POST.get('email')
    requested_format = request.POST.get('dataformat')
    job = QueuedJob.create(None, None, requested_format, email, querystring)
    job.save()
    dojob.delay(job)
    return HttpResponseRedirect('status')
