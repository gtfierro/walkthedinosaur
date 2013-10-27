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

TABLEFORPOSTVAR = {'pri-title':'patent', 'pri-id':'patent', 'pri-year':'patent', 'pri-month':'patent', 'pri-day':'patent',
                   'pri-city':'location', 'pri-state':'location', 'pri-country':'location',
                   'inv-name':'inventor', 'inv-nat':'inventor',
                   'inv-city':'location', 'inv-state':'location', 'inv-country':'location',
                   'ass-type':'assignee', 'ass-name':'assignee', 'ass-nat':'assignee', 'ass-org':'assignee', 'ass-nat':'assignee',
                   'ass-city':'location', 'ass-state':'location', 'ass-country':'location',
                   'law-name':'lawyer', 'law-org':'lawyer', 'law-country':'lawyer',
                   'cl-id':'claim', 'cl-text':'claim', 'cl-seq-d':'claim', 'cl-seq':'claim',
                   'cit-id':'uspatentcitation', 'cit-id-pa':'uspatentcitation', 'cit-year':'uspatentcitation', 'cit-day':'uspatentcitation', 'cit-month':'uspatentcitation', 'cit-country':'uspatentcitation', 'cit-seq':'uspatentcitation'}
COLUMNFORPOSTVAR = {}

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

class TestQuery(models.Model):
    def __init__(postvar):
        self.colsToSearch = []
        self.tablesToSearch = []
        self.colsFilters = []
        self.postVar = postvar;
        self.haveLoc = {'inv':0, 'ass':0}
        self.haveDate = {'pri':0, 'cit':0}
        self.locCities = {'inv':"", 'ass':""}
        self.locStates = {'inv':"", 'ass':""}
        self.locCountries = {'inv':"", 'ass':""}
        self.priDay = {'from':'', 'to':''}
        self.citDay = {'from':'', 'to':''}
        self.priMonth = {'from':'', 'to':''}
        self.citMonth = {'from':'', 'to':''}
        self.priYear = {'from':'', 'to':''}
        self.citYear = {'from':'', 'to':''}
        self.dateDays = {'pri':priDay, 'cit':citDay}
        self.dateMonths = {'pri':priMonth, 'cit':citMonth}
        self.dateYears = {'pri':priYear, 'cit':citYear}

    def getQueryString(self):
        self.updateTablesToSearch()
        self.updateColsToSearch()
        self.updateColsFilters()
        query = "SELECT "
        if len(self.colsToSearch) == 0:
            query += "* "
        else:
            i = 0
            for col in self.colsToSearch:
                if (col != '') or (self.tablesToSearch[i] != '') or (self.colsFilters[i] != ''):
                    if i < len(colsToSearch):
                        query += col + ", "
                    else:
                        query += col + " "
                i += 1
        query += "FROM "
        if len(self.tablesToSearch) == 0:
            query += " "
        else:
            i = 0
            for table in self.tablesToSearch:
                if (colsToSearch[i] != '') or (table != '') or (self.colsFilters[i] != ''):
                    if i < len(tablesToSearch):
                        query += table + ", "
                    else:
                        query += table + " "
                i += 1
        query += "WHERE "
        if len(self.colsFilters) == 0:
            query += " "
        else:
            i = 0
            for f in self.colsFilters:
                if (colsToSearch[i] != '') or (self.tablesToSearch[i] != '') or (f != ''):
                    if i < len(colsFilters):
                        query += f + ", "
                    else:
                        query += f + " "
                i += 1
        query += ";"
        return query

    def isDate(self, string):
        prefix = string.split('-')[0]
        suffix = string.split('-')[1]
        if (prefix == 'pri') or (prefix == 'cit'):
            if (suffix == 'month') or (suffix == 'year') or (suffix == 'day'):
                return True
        else:
            return False

    def isLoc(self, string):
        prefix = string.split('-')[0]
        suffix = string.split('-')[1]
        if (prefix == 'inv') or (prefix == 'ass'):
            if (suffix == 'country') or (suffix == 'city') or (suffix == 'state'):
                return True
        else:
            return False

    def getLocFilter(self, prefix, table, column):
        if (haveLoc[prefix] == 3):
            city = locCities[prefix]
            state = locStates[prefix]
            country = locCountries[prefix]
            filters = []
            if (city):
                filters.append("(location.city like " + city + "%)")
            if state:
                filters.append("(location.state like " + state + "%)")
            if country:
                filters.append("(location.country like " + country + "%)")
            filterString = "("
            i = 0
            for f in filters:
                if i != 0:
                    filterString += f
                else:
                    filterString += " AND " + f
                i += 1
            if prefix == 'inv':
                a = 1 # CHANGE THIS!
            elif prefix == 'ass':
                a = 1 # CHANGE THIS!
            else:
                print "Error! Wrong type of thing being searched for locaiton!"
            filterstring += ")"
            return filterString
        else:
            return ""

    def getDateFilter(self, prefix, table, column):
        if (haveDate[prefix] == 6):
            fromDay = dateDays[prefix]['from']
            fromMonth = dateMonths[prefix]['from']
            fromYear = dateYears[prefix]['from']
            toDay = dateDays[prefix]['to']
            toMonth = dateMonths[prefix]['to']
            toYear = dateYears[prefix]['to']
            fromDateString = fromYear + "-" + fromMonth + "-" + fromDay
            toDateString = toYear + "-" + toMonth + "-" + toDay
            return "(date(",table,".",column,") BETWEEN date(",fromDateString,") AND date(", toDateString,"))"
        elif haveDate[prefix] > 6:
            print "Error, counted date of ", prefix, " too many times!"
        else:
            return ""


    def updateColsToSearch(self):
        i = 0
        for key in self.postVar.keys():
            if (self.postVar[key] == '') or (self.postVar[key] == 'email') or (self.postVar[key] == 'dataformat'):
                colsToSearch.append('')
            else:
                if not COLUMNFORPOSTVAR[key]:
                    print "Error, case for col for ", key, " not handled!"
                else:
                    colsToSearch.append(tablesToSearch[i]+"."+COLUMNFORPOSTVAR[key])
            i += 1

    def updateTablesToSearch(self):
        for key in self.postVar.keys():
            if (self.postVar[key] == '') or (self.postVar[key] == 'email') or (self.postVar[key] == 'dataformat'):
                tablesToSearch.append('')
            else:
                if not COLUMNFORPOSTVAR[key]:
                    print "Error, case for table for ", key, " not handled!"
                else:
                    tablesToSearch.append(TABLEFORPOSTVAR[key])

    def updateColsFilters(self):
        i = 0
        for key in self.postVar.keys():
            if (self.postVar[key] == '') or (self.postVar[key] == 'email') or (self.postVar[key] == 'dataformat'):
                colsFilters.append('')
            elif self.isDate(self.postVar[key]) or self.isLoc(self.postVar[key]):
                prefix = self.postVar[key].split('-')[0]
                suffix = self.postVar[key].split('-')[1]
                if self.isDate(self.postVar[key]):
                    postfix = self.postVar[key].split('-')[2]
                    haveDate[prefix] += 1
                    if suffix == 'month':
                        dateMonths[prefix][postfix] = self.postVar[key]
                    elif suffix == 'day':
                        dateDays[prefix][postfix] = self.postVar[key]
                    elif suffix == 'year':
                        dateDays[key][postfix] = self.postVar[key]
                    else:
                        print "Error! Invalid input for ", prefix, " date."
                    colsFilters.append(getDateFilter(self.postVar[key].split('-')[0])) 
                else:
                    haveLoc[prefix] += 1
                    if suffix == 'city':
                        locCities[prefix] = self.postVar[key]
                    elif suffix == 'state':
                        locStates[prefix] = self.postVar[key]
                    elif suffix == 'country':
                        locCountries[prefix] = self.postVar[key]
                    else:
                        print "Error! Invalid input for ", prefix, " location."
                    colsFilters.append(getLocFilter(self.postVar[key].split('-')[0]))
            else:
                if not COLUMNFORPOSTVAR[key]:
                    print "Error, case for col=", key, " not handled!"
                else:
                    colsFilters.append(tablesToSearch[i]+"."+colsToSearch[i]+"="+self.postVar[key])
                
