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

POSTVARMAPS = {'pri-title':('patent', 'title'), 
               'pri-id':('patent','id'),
               'pri-date':('patent', 'date'), 
               'pri-year-from':('patent','date'), 
               'pri-month-from':('patent','date'), 
               'pri-day-from':('patent','date'), 
               'pri-year-to':('patent','date'), 
               'pri-month-to':('patent','date'), 
               'pri-day-to':('patent','date'), 
               'pri-country':('patent','country'),
               'inv-name-first':('rawinventor', 'name_first'), 
               'inv-name-last':('rawinventor', 'name_last'), 
               'inv-nat':('rawinventor', 'nationality'),
               'inv-loc':('rawlocation', 'location_id'),
               'inv-city':('rawlocation', 'city'), 
               'inv-state':('rawlocation', 'state'), 
               'inv-country':('rawlocation', 'country'),
               'ass-type':('rawassignee','type'), 
               'ass-name-first':('rawassignee','name_first'), 
               'ass-name-last':('rawassignee','name_last'), 
               'ass-nat':('rawassignee','nationality'), 
               'ass-org':('rawassignee','organization'),
               'ass-loc':('rawlocation','location_id'),
               'ass-city':('rawlocation','city'), 
               'ass-state':('rawlocation','state'), 
               'ass-country':('rawlocation','country'),
               'law-name-first':('rawlawyer','name_first'), 
               'law-name-last':('rawlawyer','name_last'), 
               'law-org':('rawlawyer','organization'), 
               'law-country':('rawlawyer','country'),
               'cl-id':('claim','patent_id'), 
               'cl-text':('claim','text'), 
               'cl-seq-d':('claim','dependent'), 
               'cl-seq':('claim','sequence'),
               'cit-id':('uspatentcitation','citation_id'), 
               'cit-id-pa':('uspatentcitation','patent_id'),
               'cit-date':('uspatentcitation','date'), 
               'cit-year-from':('uspatentcitation','date'), 
               'cit-day-from':('uspatentcitation','date'), 
               'cit-month-from':('uspatentcitation','date'), 
               'cit-year-to':('uspatentcitation','date'), 
               'cit-day-to':('uspatentcitation','date'), 
               'cit-month-to':('uspatentcitation','date'), 
               'cit-country':('uspatentcitation','country'), 
               'cit-seq':('uspatentcitation','sequence')
              }

JOINS = {('patent', 'rawinventor'):('id','patent_id'),
         ('patent', 'rawassignee'):('id','patent_id'),
         ('patent', 'claim'):('id','patent_id'),
         ('patent', 'uspatentcitation'):('id','patent_id'),
         ('rawassignee', 'rawlocation'):('rawlocation_id','id'),
         ('rawinventor', 'rawlocation'):('rawlocation_id','id')
        }


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
        self.fieldTables = []
        self.filterTables = []
        self.joinPairs = []
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
        self.updateJoins()
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

    def isField(self, string):
        prefix = string.split('-')[0]
        return prefix == 'f'

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
            return ' = '
        return ' LIKE '

    def getLocFilter(self, prefix):
        if (self.haveLoc[prefix] >= 1):
            city = self.locCities[prefix]
            state = self.locStates[prefix]
            country = self.locCountries[prefix]
            filters = []
            if city:
                filters.append("(rawlocation.city LIKE '%" + city + "%')")
            if state:
                filters.append("(rawlocation.state LIKE '%" + state + "%')")
            if country:
                filters.append("(rawlocation.country LIKE '%" + country + "%')")
            filterString = "("
            i = 0
            for f in filters:
                if i == 0:
                    filterString += f
                else:
                    filterString += " AND " + f
                i += 1
            if prefix == 'inv':
                filterString += " AND rawlocation.id = rawinventor.rawlocation_id"
                self.tablesToSearch.append('rawinventor')
                self.filterTables.append('rawinventor')
            elif prefix == 'ass':
                filterString += " AND rawlocation.id = rawassignee.rawlocation_id"
                self.tablesToSearch.append('rawassignee')
                self.tablesToSearch.append('rawassignee')
            else:
                print "Error! Wrong type of thing being searched for locaiton!"
            filterString += ")"
            self.tablesToSearch.append("rawlocation")
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
            res = "("+table+"."+column+" BETWEEN '"+fromDateString+"' AND '"+toDateString+"')"
            self.filterTables.append(table)
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
                pass
            elif self.isField(key):
                parts = key.split('-')
                parts.remove('f')
                newKey = '-'.join(parts)
                val = POSTVARMAPS[newKey]
                self.colsToSearch.append(val[0]+"."+val[1])
                self.fieldTables.append(val[0])

    def updateTablesToSearch(self):
        for key in self.postVar.keys():
            key = key.encode('ascii')
            pv = self.postVar[key].encode('ascii')
            if (pv == '') or (key == 'email') or (key == 'dataformat') or (key == 'csrfmiddlewaretoken'):
                pass
            else:
                if self.isField(key):
                    parts = key.split('-')
                    parts.remove('f')
                    newKey = '-'.join(parts)
                    self.fieldTables.append(POSTVARMAPS[newKey][0])
                else:
                    newKey = key
                self.tablesToSearch.append(POSTVARMAPS[newKey][0])
                
    def updateColsFilters(self):
        keys = self.postVar.keys()
        keys.sort()
        for key in keys:
            key = key.encode('ascii')
            pv = self.postVar[key].encode('ascii')
            if (pv == '') or (key == 'email') or (key == 'dataformat') or (key == 'csrfmiddlewaretoken') or self.isField(key):
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
                    self.colsFilters.append(self.getDateFilter(prefix, POSTVARMAPS[key][0], POSTVARMAPS[key][1])) 
                else:
                    self.haveLoc[prefix] += 1
                    if suffix == 'city':
                        self.locCities[prefix] = pv
                    elif suffix == 'state':
                        self.locStates[prefix] = pv
                    elif suffix == 'country':
                        self.locCountries[prefix] = pv
                    else:
                        print "Error! Invalid input for ", prefix, " location."
                    self.colsFilters.append(self.getLocFilter(prefix))
            else:
                if not POSTVARMAPS[key]:
                    print "Error, case for col=", key, " not handled!"
                else:
                    comparator = self.getComparator(key)
                    val = POSTVARMAPS[key]
                    self.filterTables.append(val[0])
                    if comparator == " LIKE ":
                        self.colsFilters.append("("+val[0]+"."+val[1]+comparator+"'%"+pv+"%'"+")")
                    else:
                        self.colsFilters.append("("+val[0]+"."+val[1]+comparator+pv+" )")

    def updateJoins(self):
        fdt = list(set(self.fieldTables))
        ftt = list(set(self.filterTables))
        for t1 in fdt:
            for t2 in ftt:
                if (t1,t2) in JOINS.keys():
                    print "(",t1,", ",t2,")"
                    val = JOINS[(t1,t2)]
                    self.colsFilters.append("("+t1+"."+val[0]+" = "+t2+"."+val[1]+")")
        for t1 in ftt:
            for t2 in fdt:
                if (t1,t2) in JOINS.keys():
                    print "(",t1,", ",t2,")"
                    val = JOINS[(t1,t2)]
                    self.colsFilters.append("("+t1+"."+val[0]+" = "+t2+"."+val[1]+")")