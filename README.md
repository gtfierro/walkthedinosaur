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

Make sure to edit the `walkthedinosaur/settings.py` file to send email:

```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # or some other backend
EMAIL_HOST = '' # For example, smtp.gmail.com if you are using Gmail. 
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your email here'
EMAIL_HOST_PASSWORD = 'your password here'
```


Then, create the relevant tables and start the Django server:

```
python manage.py syncdb
python manage.py runserver
```

To get the jobs to complete, first edit the config.ini file, then 
run the following in another window:

```
python run_jobs.py
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
