from celery import Celery

app = Celery('tasks', broker='redis://localhost')

from django.conf import settings

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'walkthedinosaur.settings'

from batchsql import models
from django.core.mail import send_mail
import connection
import config
from sqlalchemy.orm import sessionmaker
from uuid import uuid1
import csv
from unidecode import unidecode
import time
import threading
import socket
import config
import urllib
import re
from sqlalchemy.exc import OperationalError, DatabaseError, TimeoutError, DisconnectionError
from celery.exceptions import MaxRetriesExceededError

local = config.get_config(config.cfgfile)['local']
IP_ADDRESS = ""
FILESERVER_PORT = config.get_config(config.cfgfile)['port']
if local:
    IP_ADDRESS = socket.gethostbyname(socket.gethostname())
else:
    f = urllib.urlopen("http://www.canyouseeme.org/")
    html_doc = f.read()
    f.close()
    m = re.search('(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',html_doc)
    IP_ADDRESS = m.group(0)

Session = sessionmaker(bind=connection.engine)
session = Session()

def create_output(job, result):
    filename = 'finished_jobs/'+str(uuid1())
    if job.requested_format == 'CSV':
        filename += '.csv'
        w = csv.writer(open(filename, 'w'))
        for row in result:
            row = filter(lambda x: x, row)
            row = [unidecode(unicode(x)) for x in row]
            w.writerow(row)
    elif job.requested_format == 'TSV':
        filename += '.tsv'
        w = csv.writer(open(filename, 'w'), delimiter='\t')
        for row in result:
            row = filter(lambda x: x, row)
            row = [unidecode(unicode(x)) for x in row]
            w.writerow(row)
    return filename

def get_job():
    conn = connection.engine.connect()
    if models.QueuedJob.objects.count() > 0:
        return models.QueuedJob.objects.all().order_by('id')[0]
    return None

def run_job(job):
    query = job.query_string
    result = session.execute(query)
    filename = create_output(job, result)
    return filename

def update_job_listing(job, filename, status, error=''):
    if status == 'Executing':
        job.job_status = 'Executing'
        job.save()
    else:
        cj = models.CompletedJob.create(job, filename, status, error)
        models.QueuedJob.objects.filter(pk=job.id).delete()
        cj.save()

EMAIL_TEMPLATE = """
Hello,

Your batch SQL job {0} running the query "{1}" has finished. Please download at {2}.

- Fung Institute Patent Group
"""

ERROR_EMAIL_TEMPLATE = """
Hello,

Your batch SQL job {0} running the query "{1}" has been halted.

We are very sorry for the onconvenience. If you have any questions, please email patentinterface@gmail.com.

- Fung Institute Patent Group
"""

def send_notification(job, filename='', successful=False):
    subject = 'Job {0} has finished'.format(job.id)
    port = FILESERVER_PORT
    from_email = 'fungpat@berkeley.edu'
    to_email = [job.destination_email]
    if (successful):
        port = FILESERVER_PORT
        url = "http://{0}:{1}/{2}".format(IP_ADDRESS, port, filename[14:])
        if not local:
            url = "http://{0}/{1}".format(IP_ADDRESS, filename)
        message = EMAIL_TEMPLATE.format(job.id, job.query_string, url)
    else:
        message = ERROR_EMAIL_TEMPLATE.forma(job.id, job.query_string)
    send_mail(subject, message, from_email, to_email, fail_silently=False)
    #mail_thread = threading.Thread(target = send_mail, args=(subject, message, from_email, to_email), kwargs={"fail_silently":False})
    #mail_thread.start()
    #mail_thread.join()

@app.task(max_retries=3)
def dojob(job):
    try:
        update_job_listing(job, '', 'Executing')
        filename = run_job(job)
    except (OperationalError, DatabaseError, TimeoutError, DisconnectionError) as e:
        update_job_listing(job, '', 'Halted', str(e))
        try:
            send_notification(job)
        except:
            return
        return

# The previous method did not do anything if task failed. Which is why I removed retry 
# and updated to halted and returned. No returning causes error in send_notification as no
# filename has been estabilished.       
#        try:
#            dojob.retry(args=(job,), exc=e, countdown=5)
#        except MaxRetriesExceededError as e:
#            update_job_listing(job, '', 'Halted', str(e))
    try:
        send_notification(job, filename, True)
    except Exception as e:
        update_job_listing(job, filename, 'Could Not send Email', str(e))
    update_job_listing(job, filename, 'Completed')

#while True:
#    print 'Attempting to get job...'
#    job = get_job()
#    if job:
#        print 'Got job', job.id
#        print 'Running job', job.id
#        filename = run_job(job)
#        print 'Finished running job', job.id
#        print 'Notifying user...'
#        send_notification(job, filename)
#        print 'Updating job listing...'
#        update_job_listing(job, filename)
#        print 'Finished'
#    else:
#        print 'Could not find job. Retrying in 5...'
#        time.sleep(5)
