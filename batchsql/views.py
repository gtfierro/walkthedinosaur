from django.http import HttpResponse, HttpResponseRedirect 
from django.core.urlresolvers import reverse
from django.shortcuts import render
from tasks import dojob
from uuid import uuid1
from datetime import datetime

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

# Escapes all quotes, double-quotes and escapes
def escape(s):
    s = s.replace("'", "\\'")
    s = s.replace('"','\\"')
    s = s.replace("\\", "\\\\")
    return s

def index(request):
    context = {'page': 'home'}
    return render(request, 'batchsql/index.html', context)

def status(request):
    number_of_queries = len(QueuedJob.objects.all())
    number_of_finished = len(CompletedJob.objects.all())
    context = {'number_of_queries': number_of_queries,
               'jobs': QueuedJob.objects.all().order_by('-date_submitted'),
               'number_of_finished': number_of_finished,
               'cjobs':CompletedJob.objects.all().order_by('-date_completed'),
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
    job = QueuedJob.create(tablename, fields, requested_format, email, querystring, 'In Queue')
    job.save()
    return HttpResponseRedirect('status')

def test(request):
    context = {'tables': tables, 'months':months, 'years':years, 'days':days, 
               'page': 'query'}
    return render(request, 'batchsql/test.html', context)

def submit_test(request):
    newQuery = TestQuery(request.POST)
    querystring, isValid = newQuery.getQueryString()
    email = escape(request.POST.get('email'))
    requested_format = escape(request.POST.get('dataformat'))
    if (isValid):
        job = QueuedJob.create(None, None, requested_format, email, querystring, 'In Queue')
        job.save()
        dojob.delay(job)
    else:
        job = CompletedJob(query_string = querystring, 
                           requested_format = requested_format,
                           destination_email = email,
                           date_submitted = datetime.now(),
                           date_completed = datetime.now(),
                           old_jobid = str(uuid1()),
                           result_filename = "",
                           job_status = "Halted",
                           job_error = "Cannot query more than 4 tables!")
        job.save()
    return HttpResponseRedirect('status')
