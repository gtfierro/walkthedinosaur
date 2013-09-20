from django.http import HttpResponse, HttpResponseRedirect 
from django.core.urlresolvers import reverse
from django.shortcuts import render

from batchsql.models import QueuedJob, CompletedJob
import connection
tables = connection.tables

def index(request):
    number_of_queries = len(QueuedJob.objects.all())
    number_of_finished = len(CompletedJob.objects.all())
    context = {'number_of_queries': number_of_queries,
               'number_of_finished': number_of_finished}
    return render(request, 'batchsql/index.html', context)

def define_query(request):
    context = {'tables': tables}
    return render(request, 'batchsql/define.html', context)

def submit_query(request):
    tablename = request.POST['tablename']
    fields = request.POST.getlist('fields')
    email = request.POST.get('email')
    requested_format = request.POST.get('dataformat')
    job = QueuedJob.create(tablename, fields, requested_format, email)
    job.save()
    return HttpResponseRedirect('index')
