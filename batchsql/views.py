from django.http import HttpResponse
from django.shortcuts import render

from batchsql.models import QueuedJob
import connection

def index(request):
    number_of_queries = len(QueuedJob.objects.all())
    context = {'number_of_queries': number_of_queries}
    return render(request, 'batchsql/index.html', context)

def define_query(request):
    tables = connection.tables
    context = {'tables': tables}
    return render(request, 'batchsql/define.html', context)
