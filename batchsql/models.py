from django.db import models
from datetime import datetime
from uuid import uuid1

CSV = 'CSV'
TSV = 'TSV'
SQL = 'SQL'
FORMAT_CHOICES = (
    (CSV, 'Comma-separated values'),
    (TSV, 'Tab-separated values'),
    (SQL, 'Sqlite file')
)

class QueuedJob(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    date_submitted = models.DateTimeField(default=datetime.now())
    query_string = models.TextField()
    requested_format = models.CharField(max_length=3,
                                        choices=FORMAT_CHOICES,
                                        default=CSV)
    destination_email = models.CharField(max_length=50)

    @classmethod
    def create(klass, tablename, fields, requested_format, destination_email, querystring):
        if not querystring:
            querystring = "select {0} from {1};".format(','.join(fields), tablename)
        job = QueuedJob(id = str(uuid1()),
                        query_string = querystring,
                        requested_format = requested_format,
                        destination_email = destination_email)
        return job

class CompletedJob(models.Model):
    old_jobid = models.CharField(max_length=50)
    date_submitted = models.DateTimeField()
    date_completed = models.DateTimeField(default=datetime.now())
    query_string = models.TextField()
    requested_format = models.CharField(max_length=3,
                                        choices=FORMAT_CHOICES,
                                        default=CSV)
    destination_email = models.CharField(max_length=50)
    result_filename = models.CharField(max_length=50)

    @classmethod
    def create(klass, qj, result_filename):
        job = CompletedJob(query_string = qj.query_string,
                           requested_format = qj.requested_format,
                           destination_email = qj.destination_email,
                           date_submitted = qj.date_submitted,
                           old_jobid = qj.id,
                           result_filename = result_filename)
        return job
