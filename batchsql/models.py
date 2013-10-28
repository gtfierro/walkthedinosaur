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

TABLEFORPOSTVAR = {'pri-title':'patent', 'pri-id':'patent', 'pri-year-from':'patent', 'pri-month-from':'patent', 'pri-day-from':'patent', 'pri-year-to':'patent', 'pri-month-to':'patent', 'pri-day-to':'patent', 'pri-country':'patent',
                   'inv-name-first':'inventor', 'inv-name-last':'inventor', 'inv-nat':'inventor',
                   'inv-city':'location', 'inv-state':'location', 'inv-country':'location',
                   'ass-type':'assignee', 'ass-name-first':'assignee', 'ass-name-last':'assignee', 'ass-nat':'assignee', 'ass-org':'assignee',
                   'ass-city':'location', 'ass-state':'location', 'ass-country':'location',
                   'law-name-first':'lawyer', 'law-name-last':'lawyer', 'law-org':'lawyer', 'law-country':'lawyer',
                   'cl-id':'claim', 'cl-text':'claim', 'cl-seq-d':'claim', 'cl-seq':'claim',
                   'cit-id':'uspatentcitation', 'cit-id-pa':'uspatentcitation', 'cit-year-from':'uspatentcitation', 'cit-year-to':'uspatentcitation', 'cit-day-from':'uspatentcitation', 'cit-month-from':'uspatentcitation', 'cit-day-to':'uspatentcitation', 'cit-month-to':'uspatentcitation', 'cit-country':'uspatentcitation', 'cit-seq':'uspatentcitation'}
COLUMNFORPOSTVAR = {'pri-title':'title', 'pri-id':'id', 'pri-year-from':'date', 'pri-month-from':'date', 'pri-day-from':'date', 'pri-year-to':'date', 'pri-month-to':'date', 'pri-day-to':'date', 'pri-country':'country',
                   'inv-name-first':'name_first', 'inv-name-last':'name_last', 'inv-nat':'nationality',
                   'inv-city':'city', 'inv-state':'state', 'inv-country':'country',
                   'ass-type':'type', 'ass-name-first':'name_first', 'ass-name-last':'name_last', 'ass-nat':'nationality', 'ass-org':'organization',
                   'ass-city':'city', 'ass-state':'state', 'ass-country':'country',
                   'law-name-first':'name_first', 'law-name-last':'name_last', 'law-org':'organization', 'law-country':'country',
                   'cl-id':'patent_id', 'cl-text':'text', 'cl-seq-d':'dependent', 'cl-seq':'sequence',
                   'cit-id':'citation_id', 'cit-id-pa':'patent_id', 'cit-year-from':'date', 'cit-day-from':'date', 'cit-month-from':'date', 'cit-year-to':'date', 'cit-day-to':'date', 'cit-month-to':'date', 'cit-country':'country', 'cit-seq':'sequence'}

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
    def __init__(self, postvar):
        self.colsToSearch = []
        self.tablesToSearch = []
        self.colsFilters = []
        self.postVar = postvar;
        self.haveLoc = {'inv':0, 'ass':0}
        self.haveDate = {'pri':0, 'cit':0}
        self.locCities = {'inv':'', 'ass':''}
        self.locStates = {'inv':'', 'ass':''}
        self.locCountries = {'inv':'', 'ass':''}
        self.priDay = {'from':'', 'to':''}
        self.citDay = {'from':'', 'to':''}
        self.priMonth = {'from':'', 'to':''}
        self.citMonth = {'from':'', 'to':''}
        self.priYear = {'from':'', 'to':''}
        self.citYear = {'from':'', 'to':''}
        self.dateDays = {'pri':self.priDay, 'cit':self.citDay}
        self.dateMonths = {'pri':self.priMonth, 'cit':self.citMonth}
        self.dateYears = {'pri':self.priYear, 'cit':self.citYear}

    def getQueryString(self):
        self.updateTablesToSearch()
        self.updateColsToSearch()
        self.updateColsFilters()
        query = "SELECT "
        if len(self.colsToSearch) == 0:
            query += "* "
        else:
            cts = list(set(self.colsToSearch))
            if ('' in cts): cts.remove('')
            i = 0
            for col in cts:
                if i < len(cts) - 1:
                    query += col + ", "
                else:
                    query += col + " "
                i += 1
        query += "FROM "
        if len(self.tablesToSearch) == 0:
            query += " "
        else:
            tts = list(set(self.tablesToSearch))
            if ('' in tts): tts.remove('')
            i = 0
            for table in tts:
                if i < len(tts) - 1:
                    query += table + ", "
                else:
                    query += table + " "
                i += 1
        if self.haveLoc['inv'] or self.haveLoc['ass']:
            query += ", location_inventor, location_assignee "
        query += "WHERE "
        if len(self.colsFilters) == 0:
            query += " "
        else:
            cf = list(set(self.colsFilters))
            if ('' in cf): cf.remove('')
            i = 0
            for f in cf:
                if i < len(cf) - 1:
                    print "query = ", query
                    print "f = ", f
                    query += f + " AND "
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

    def getComparator(self, key):
        numbers = ['pri-id', 'cl-id', 'cl-seq-d', 'cl-seq', 'cit-seq']
        if key in numbers:
            return ' == '
        return ' LIKE '

    def getLocFilter(self, prefix, table, column):
        if (self.haveLoc[prefix] >= 1):
            city = self.locCities[prefix]
            state = self.locStates[prefix]
            country = self.locCountries[prefix]
            filters = []
            if (city):
                filters.append("(location.city LIKE '%" + city + "%')")
            if state:
                filters.append("(location.state LIKE '%" + state + "%')")
            if country:
                filters.append("(location.country LIKE '%" + country + "%')")
            filterString = "("
            i = 0
            for f in filters:
                if i != 0:
                    filterString += f
                else:
                    filterString += " AND " + f
                i += 1
            if prefix == 'inv':
                filterString += ", location.id == location_inventor.id"
            elif prefix == 'ass':
                filterString += ", location.id == location_assignee.id"
            else:
                print "Error! Wrong type of thing being searched for locaiton!"
            filterstring += ")"
            return filterString
        else:
            return ""

    def getDateFilter(self, prefix, table, column):
        if (self.haveDate[prefix] == 6):
            fromDay = self.dateDays[prefix]['from']
            fromMonth = self.dateMonths[prefix]['from']
            fromYear = self.dateYears[prefix]['from']
            toDay = self.dateDays[prefix]['to']
            toMonth = self.dateMonths[prefix]['to']
            toYear = self.dateYears[prefix]['to']
            fromDateString = fromYear + '-' + fromMonth + '-' + fromDay
            toDateString = toYear + '-' + toMonth + '-' + toDay
            res = '(date('+table+'.'+column+') BETWEEN date('+fromDateString+') AND date('+toDateString+'))'
            return res
        elif self.haveDate[prefix] > 6:
            print 'Error, counted date of ', prefix, ' too many times!'
        else:
            return ''


    def updateColsToSearch(self):
        for key in self.postVar.keys():
            key = key.encode('ascii')
            pv = self.postVar[key].encode('ascii')
            if (pv == '') or (key == 'email') or (key == 'dataformat') or (key == 'csrfmiddlewaretoken'):
                self.colsToSearch.append('')
            else:
                if not COLUMNFORPOSTVAR[key]:
                    print "Error, case for col for ", key, " not handled!"
                else:
                    self.colsToSearch.append(TABLEFORPOSTVAR[key]+"."+COLUMNFORPOSTVAR[key])

    def updateTablesToSearch(self):
        for key in self.postVar.keys():
            key = key.encode('ascii')
            pv = self.postVar[key].encode('ascii')
            if (pv == '') or (key == 'email') or (key == 'dataformat') or (key == 'csrfmiddlewaretoken'):
                self.tablesToSearch.append('')
            else:
                if not COLUMNFORPOSTVAR[key]:
                    print "Error, case for table for ", key, " not handled!"
                else:
                    self.tablesToSearch.append(TABLEFORPOSTVAR[key])

    def updateColsFilters(self):
        for key in self.postVar.keys():
            key = key.encode('ascii')
            pv = self.postVar[key].encode('ascii')
            if (pv == '') or (key == 'email') or (key == 'dataformat') or (key == 'csrfmiddlewaretoken'):
                self.colsFilters.append('')
            elif self.isDate(key) or self.isLoc(key):
                prefix = key.split('-')[0]
                suffix = key.split('-')[1]
                if self.isDate(key):
                    postfix = key.split('-')[2]
                    self.haveDate[prefix] += 1
                    if suffix == 'month':
                        self.dateMonths[prefix][postfix] = pv
                    elif suffix == 'day':
                        self.dateDays[prefix][postfix] = pv
                    elif suffix == 'year':
                        self.dateYears[prefix][postfix] = pv
                    else:
                        print "Error! Invalid input for ", prefix, " date."
                    self.colsFilters.append(self.getDateFilter(prefix, TABLEFORPOSTVAR[key], COLUMNFORPOSTVAR[key])) 
                else:
                    self.haveLoc[prefix] += 1
                    if suffix == 'city':
                        locCities[prefix] = pv
                    elif suffix == 'state':
                        locStates[prefix] = pv
                    elif suffix == 'country':
                        locCountries[prefix] = pv
                    else:
                        print "Error! Invalid input for ", prefix, " location."
                    self.colsFilters.append(getLocFilter(prefix, TABLEFORPOSTVAR[key], COLUMNFORPOSTVAR[key]))
            else:
                if not COLUMNFORPOSTVAR[key]:
                    print "Error, case for col=", key, " not handled!"
                else:
                    comparator = self.getComparator(key)
                    self.colsFilters.append("("+TABLEFORPOSTVAR[key]+"."+COLUMNFORPOSTVAR[key]+comparator+"'%"+pv+"%'"+")")

