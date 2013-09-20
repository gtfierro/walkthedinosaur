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

Then, create the relevant tables and start the Django server:

```
python manage.py syncdb
python manage.py runserver
```

To get the jobs to complete, run the following in another window:

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

or use the provided Go fileserver. Note tha

```
go build fileserver.go
./fileserver
```

You can access the Django app via [http://localhost:8000/batchsql](http://localhost:8000/batchsql).
Files are served via [http://localhost:8080]
