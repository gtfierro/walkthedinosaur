from django.db import models
from datetime import datetime

CSV = 'CSV'
TSV = 'TSV'
SQL = 'SQL'
FORMAT_CHOICES = (
    (CSV, 'Comma-separated values'),
    (TSV, 'Tab-separated values'),
    (SQL, 'Sqlite file')
)

class QueuedJob(models.Model):
    date_submitted = models.DateTimeField(default=datetime.now())
    query_string = models.TextField()
    requested_format = models.CharField(max_length=3,
                                        choices=FORMAT_CHOICES,
                                        default=CSV)
    destination_email = models.CharField(max_length=50)

    @classmethod
    def create(klass, tablename, fields):
        querystring = "select {0} from {1};".format(','.join(fields), tablename)
        job = QueuedJob(query_string = querystring,
                        destination_email = 'a@a.com')
        return job

class CompletedJob(models.Model):
    date_submitted = models.DateTimeField()
    date_completed = models.DateTimeField()
    query_string = models.TextField()
    requested_format = models.CharField(max_length=3,
                                        choices=FORMAT_CHOICES,
                                        default=CSV)
    destination_email = models.CharField(max_length=50)
