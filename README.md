walkthedinosaur
===============

Web-interface for specifying SQL queries that are executed as batch jobs.

* Specify some sort of query on the web side
    * arbitrary query support? need to make database read-only
* this gets queued up
* query is executed, results are cached serverside
* temporary download link is sent to user via email
* option to download as CSV, sqlite3, TSV, etc
* user accounts

## How to Use

To set up the Django app, first make sure you have all the dependencies installed by running

```
pip install -r requirements.txt
```

Keep in mind that this does not install the following packages at the time of this commit:  

```
redis-server 	  (apt-get install redis-server)
sentry 		  (pip install django-sentry)
virtualenv 	  (pip install virtualenv)
raven 		  (pip install raven)
apache2 	  (apt-get isntall apache2)
mos_wsgi  	  (apt-get install libapache2-mod-wsgi)
```

Make sure to add a file in the 'walkthedinosaur/' directory with the email settings and your private key 
for the server (and any other private settings you many want).

```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # or some other backend
EMAIL_HOST = '' # For example, smtp.gmail.com if you are using Gmail.
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your email here'
EMAIL_HOST_PASSWORD = 'your password here'
```

Then, include that file's name in `walkthedinosaur/settings.py`. 
By default, the settings.py file will import all settings variables from pass_settings.py. 
To change this file's name, change the line contaning 

from pass_settings import *

and change 'pass_settings" to "filename" if your file is named "filename.py"

Then, create the relevant tables and start the Django server:

```
python manage.py syncdb
python manage.py runserver
```

To get the jobs to complete, first edit the config.ini file, then 
run the following in another window:

```
celery -A walkthedinosaur worker -l info
```

We need a redis server to act as the broker for Celery, so run the following command:

```
redis-server
```

To serve up the files, you're going to want to run a basic fileserver.
You can use the provided Python one:

```
mkdir finished_jobs
cd finished_jobs
python -m SimpleHTTPServer 8080
```
This runs the server on port 8080. Please specify the port in config.ini file.

or use the provided Go fileserver. Note tha

```
go build fileserver.go
./fileserver
```

You can access the Django app via [http://localhost:8000/batchsql](http://localhost:8000/batchsql).
Files are served via [http://localhost:8080]
