from django.http import HttpResponse, HttpResponseRedirect 
from django.core.urlresolvers import reverse
from django.shortcuts import render

from batchsql.models import QueuedJob
import connection
tables = connection.tables

def index(request):
    number_of_queries = len(QueuedJob.objects.all())
    context = {'number_of_queries': number_of_queries}
    return render(request, 'batchsql/index.html', context)

def define_query(request):
    context = {'tables': tables}
    return render(request, 'batchsql/define.html', context)

def submit_query(request):
    print request.POST
    tablename = request.POST['tablename']
    fields = request.POST.getlist('fields')
    job = QueuedJob.create(tablename, fields)
    job.save()
    return HttpResponseRedirect('index')
