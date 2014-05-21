from django.db import models
from datetime import datetime
from uuid import uuid1

import time

CSV = 'CSV'
TSV = 'TSV'
SQL = 'SQL'
FORMAT_CHOICES = (
    (CSV, 'Comma-separated values'),
    (TSV, 'Tab-separated values'),
    (SQL, 'Sqlite file')
)

# tables: patent, application, rawinventor, rawlocation, rawassignee, rawlawyer, claim, uspatentcitations

POSTVARMAPS = {'pri-title':('patent', 'title'),
               'pri-id':('patent','id'),
               'pri-date-grant':('patent', 'date'),
               'pri-date-grant-from':('patent', 'date'),
               'pri-date-grant-to':('patent', 'date'),
               'pri-date-file':('application','date'),
               'pri-date-file-from':('application', 'date'),
               'pri-date-file-to':('application', 'date'),
               'pri-country':('patent','country'),
               'inv-name-first':('rawinventor', 'name_first'),
               'inv-name-last':('rawinventor', 'name_last'),
               'inv-id':('inventor', 'id'),
               'inv-nat':('rawinventor', 'nationality'),
               'inv-loc':('rawlocation', 'location_id'),
               'inv-city':('rawlocation', 'city'),
               'inv-state':('rawlocation', 'state'),
               'inv-country':('rawlocation', 'country'),
               'ass-type':('rawassignee','type'),
               'ass-name-first':('rawassignee','name_first'),
               'ass-name-last':('rawassignee','name_last'),
               'ass-id':('assignee','id'),
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
               'cit-date-from':('uspatentcitation', 'date'),
               'cit-date-to':('uspatentcitation', 'date'),
               'cit-country':('uspatentcitation','country'),
               'cit-seq':('uspatentcitation','sequence')
              }

POSTVARMAPS_DIS = {'pri-title':('patent', 'title'),
                   'pri-id':('patent','id'),
                   'pri-date-grant':('patent', 'date'),
                   'pri-date-grant-from':('patent', 'date'),
                   'pri-date-grant-to':('patent', 'date'),
                   'pri-date-file':('application','date'),
                   'pri-date-file-from':('application', 'date'),
                   'pri-date-file-to':('application', 'date'),
                   'pri-country':('patent','country'),
                   'inv-name-first':('inventor', 'name_first'),
                   'inv-name-last':('inventor', 'name_last'),
                   'inv-id':('inventor', 'id'),
                   'inv-nat':('inventor', 'nationality'),
                   'inv-city':('location', 'city'),
                   'inv-state':('location', 'state'),
                   'inv-country':('location', 'country'),
                   'ass-type':('assignee','type'),
                   'ass-name-first':('assignee','name_first'),
                   'ass-name-last':('assignee','name_last'),
                   'ass-id':('assignee','id'),
                   'ass-nat':('assignee','nationality'),
                   'ass-org':('assignee','organization'),
                   'ass-city':('location','city'),
                   'ass-state':('location','state'),
                   'ass-country':('location','country'),
                   'law-name-first':('lawyer','name_first'),
                   'law-name-last':('lawyer','name_last'),
                   'law-org':('lawyer','organization'),
                   'law-country':('lawyer','country'),
                  }

JOINS = {('patent', 'rawinventor'):('id','patent_id'),
         ('patent', 'rawassignee'):('id','patent_id'),
         ('patent', 'claim'):('id','patent_id'),
         ('patent', 'rawlawyer'):('id','patent_id'),
         ('patent', 'uspatentcitation'):('id','patent_id'),
         ('patent', 'application'):('id','patent_id'),
         ('rawassignee', 'rawlocation'):('rawlocation_id','id'),
         ('rawassignee', 'rawlawyer'):('patent_id','patent_id'),
         ('rawassignee', 'rawinventor'):('patent_id','patent_id'),
         ('rawassignee', 'application'):('patent_id','patent_id'),
         ('rawinventor', 'application'):('patent_id','patent_id'),
         ('rawinventor', 'rawlocation'):('rawlocation_id','id'),
         ('rawinventor', 'rawlawyer'):('patent_id','patent_id'),
         ('rawlawyer','application'):('patent_id','patent_id')
        }

JOINS_DIS = {('patent','assignee'):'patent_assignee',
             ('patent','inventor'):'patent_inventor',
             ('patent','lawyer'):'patent_lawyer',
             ('location','assignee'):'location_assignee',
             ('location','inventor'):'location_inventor'
            }

ALL_POSTVARMAPS = {'raw':POSTVARMAPS,'dis':POSTVARMAPS_DIS}

ALL_JOINS = {'raw':JOINS,'dis':JOINS_DIS}

class QueuedJob(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    date_submitted = models.DateTimeField()
    query_string = models.TextField()
    requested_format = models.CharField(max_length=3,
                                        choices=FORMAT_CHOICES,
                                        default=CSV)
    destination_email = models.CharField(max_length=50)
    job_status = models.CharField(max_length=20)
    @classmethod
    def create(klass, tablename, fields, requested_format, destination_email, querystring, status):
        if not querystring:
            querystring = "select {0} from {1};".format(','.join(fields), tablename)
        job = QueuedJob(id = str(uuid1()),
                        query_string = querystring,
                        date_submitted = datetime.now(),
                        requested_format = requested_format,
                        destination_email = destination_email,
                        job_status = status)
        return job

class CompletedJob(models.Model):
    old_jobid = models.CharField(max_length=50)
    date_submitted = models.DateTimeField()
    date_completed = models.DateTimeField()
    query_string = models.TextField()
    requested_format = models.CharField(max_length=3,
                                        choices=FORMAT_CHOICES,
                                        default=CSV)
    destination_email = models.CharField(max_length=50)
    result_filename = models.CharField(max_length=50)
    job_status = models.CharField(max_length=25)
    job_error = models.CharField(max_length=300, default='')
    @classmethod
    def create(klass, qj, result_filename, status, error=''):
        job = CompletedJob(query_string = qj.query_string,
                           requested_format = qj.requested_format,
                           destination_email = qj.destination_email,
                           date_submitted = qj.date_submitted,
                           date_completed = datetime.now(),
                           old_jobid = qj.id,
                           result_filename = result_filename,
                           job_status = status,
                           job_error = error)
        return job

class TestQuery(models.Model):
    def __init__(self, postvar, dt):
        self.colsToSearch = []
        self.tablesToSearch = []
        self.colsFilters = []
        self.fieldTables = []
        self.filterTables = []
        self.postVar = postvar;
        self.postVarCopy = {}
        self.haveLoc = {'inv':0, 'ass':0}
        self.haveDate = {'file':{'count':0, 'from':'', 'to':''},
                         'cit':{'count':0, 'from':'', 'to':''},
                         'grant':{'count':0, 'from':'', 'to':''}}
        self.locCities = {'inv':'', 'ass':''}
        self.locStates = {'inv':'', 'ass':''}
        self.locCountries = {'inv':'', 'ass':''}
        self.datatype = dt;

    def getQueryString(self):
        self.escapeInput()
        self.postVar = self.postVarCopy
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
        if len(self.colsFilters) == 0:
            query += " "
        else:
            cf = list(set(self.colsFilters))
            if ('' in cf): cf.remove('')
            if len(cf) == 0:
                query += " "
            else:
                query += "WHERE "
                i = 0
                for f in cf:
                    if i < len(cf) - 1:
                        query += f + " AND "
                    else:
                        query += f + " "
                    i += 1
            query += ";"
        if (self.datatype == "dis"):
            query = query.replace("raw", "")
        if (len(list(set(self.tablesToSearch))) > 5):
            return query, False
        return query, True

    def escapeInput(self):
        for key in self.postVar.keys():
            s = self.postVar[key]
            s = s.replace("'", "\\'")
            s = s.replace('"','\\"')
            s = s.replace("\\", "\\\\")
            self.postVarCopy[key] = s

    def isField(self, string):
        prefix = string.split('-')[0]
        return prefix == 'f'

    def isDate(self, string):
        prefix = string.split('-')[0]
        suffix = string.split('-')[1]
        if ((prefix == 'pri') or (prefix == 'cit')) and (suffix == 'date'):
            return True

    def isLoc(self, string):
        prefix = string.split('-')[0]
        suffix = string.split('-')[1]
        if (prefix == 'inv') or (prefix == 'ass'):
            if (suffix == 'country') or (suffix == 'city') or (suffix == 'state') or (suffix == 'loc'):
                return True
        else:
            return False

    def getComparator(self, key):
        numbers = ['cl-id', 'cl-seq-d', 'cl-seq', 'cit-seq']
        if key in numbers:
            return ' = '
        return ' LIKE '

    def getLocFilter(self, prefix):
        if self.datatype == 'raw':
            return self.getRawLocFilter(prefix)
        return self.getDisLocFilter(prefix)

    def getDisLocFilter(self,prefix):
        if (self.haveLoc[prefix] >= 1):
            city = self.locCities[prefix]
            state = self.locStates[prefix]
            country = self.locCountries[prefix]
            filters = []
            if city:
                filters.append("(location.city = '" + city + "')")
            if state:
                filters.append("(location.state = '" + state + "')")
            if country:
                filters.append("(location.country = '" + country + "')")
            filterString = "("
            i = 0
            for f in filters:
                if i == 0:
                    filterString += f
                else:
                    filterString += " AND " + f
                i += 1
            if prefix == 'inv':
                filterString += " AND location_inventor.inventor_id = inventor.id AND location_inventor.location_id = location.id"
                self.tablesToSearch.append('inventor')
                self.tablesToSearch.append('location_inventor')
                self.filterTables.append('inventor')
            elif prefix == 'ass':
                filterString += " AND location_assignee.assignee_id = assignee.id AND location_assignee.location_id = location.id"
                self.tablesToSearch.append('assignee')
                self.tablesToSearch.append('location_assignee')
                self.filterTables.append('assignee')
            else:
                print "Error! Wrong type of thing being searched for locaiton!"
            filterString += ")"
            self.tablesToSearch.append("location")
            return filterString
        else:
            return ""

    def getRawLocFilter(self, prefix):
        if (self.haveLoc[prefix] >= 1):
            city = self.locCities[prefix]
            state = self.locStates[prefix]
            country = self.locCountries[prefix]
            filters = []
            if city:
                filters.append("(rawlocation.city = '" + city + "')")
            if state:
                filters.append("(rawlocation.state = '" + state + "')")
            if country:
                filters.append("(rawlocation.country = '" + country + "')")
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
                self.filterTables.append('rawassignee')
            else:
                print "Error! Wrong type of thing being searched for locaiton!"
            filterString += ")"
            self.tablesToSearch.append("rawlocation")
            return filterString
        else:
            return ""

    def getDateFilter(self, typeWanted, table, column, force=False):
        if (self.haveDate[typeWanted]['count'] == 2):
            fromDateString = self.haveDate[typeWanted]['from']
            toDateString = self.haveDate[typeWanted]['to']
            res = "("+table+"."+column+" BETWEEN '"+fromDateString+"' AND '"+toDateString+"')"
            self.filterTables.append(table)
            self.tablesToSearch.append(table)
            return res
        elif self.haveDate[typeWanted]['count'] > 2:
            print 'Error, counted date of ', prefix, ' too many times!'
            return ''
        elif force:
            if self.haveDate[typeWanted]['from']:
                fromDateString = self.haveDate[typeWanted]['from']
                partsOfFrom = fromDateString.split('-')
                toDateString = str(int(partsOfFrom[0])+3)+'-'+partsOfFrom[1]+'-'+partsOfFrom[2]
                res = "("+table+"."+column+" BETWEEN '"+fromDateString+"' AND '"+toDateString+"')"
                self.filterTables.append(table)
                self.tablesToSearch.append(table)
                return res
            elif self.haveDate[typeWanted]['to']:
                toDateString = self.haveDate[typeWanted]['to']
                partsOfTo = toDateString.split('-')
                fromDateString = str(int(partsOfTo[0])-3)+'-'+partsOfTo[1]+'-'+partsOfTo[2]
                res = "("+table+"."+column+" BETWEEN '"+fromDateString+"' AND '"+toDateString+"')"
                self.filterTables.append(table)
                self.tablesToSearch.append(table)
                return res
            else:
                toDateString = time.strftime('%Y-%m-%d')
                partsOfTo = toDateString.split('-')
                fromDateString = str(int(partsOfTo[0])-3)+'-'+partsOfTo[1]+'-'+partsOfTo[2]
                res = "("+table+"."+column+" BETWEEN '"+fromDateString+"' AND '"+toDateString+"')"
                self.filterTables.append(table)
                self.tablesToSearch.append(table)
                return res
        else:
            return ''

    def getTypeWanted(self, key):
        parts = key.split('-')
        if parts[0] == 'pri':
            return parts[2]
        return parts[0]

    def processDateInput(self, key, pv):
        parts = key.split('-')
        if parts[0] == 'pri':
            if parts[2] == 'file' and parts[3] == 'from':
                self.haveDate['file']['from'] = pv
                self.haveDate['file']['count'] += 1
            elif parts[2] == 'file' and parts[3] == 'to':
                self.haveDate['file']['to'] = pv
                self.haveDate['file']['count'] += 1
            elif parts[2] == 'grant' and parts[3] == 'from':
                self.haveDate['grant']['from'] = pv
                self.haveDate['grant']['count'] += 1
            elif parts[2] == 'grant' and parts[3] == 'to':
                self.haveDate['grant']['to'] = pv
                self.haveDate['grant']['count'] += 1
            else:
                print 'Cannot parse date! Invalid Key = ', key
        else:
            if parts[2] == 'from':
                self.haveDate['cit']['from'] = pv
                self.haveDate['cit']['count'] += 1
            elif parts[2] == 'to':
                self.haveDate['cit']['to'] = pv
                self.haveDate['cit']['count'] += 1
            else:
                print 'Cannot parse date! Invalid Key = ', key

    def getNewDateKey(self, key):
        keysDict = {'file':'pri-date-file',
                    'grant':'pri-date-grant',
                    'cit':'cit-date'}
        return keysDict[key]

    def updateColsToSearch(self):
        for key in self.postVar.keys():
            key = key.encode('ascii')
            pv = self.postVar[key].encode('ascii')
            if '_' in key:
                key = key.replace('_','-')
            if (pv == '') or (key == 'email') or (key == 'dataformat') or (key == 'csrfmiddlewaretoken') or (key == 'datatype'):
                pass
            elif self.isField(key):
                parts = key.split('-')
                parts.remove('f')
                newKey = '-'.join(parts)
                val = ALL_POSTVARMAPS[self.datatype][newKey]
                if self.isLoc(newKey):
                    self.colsToSearch.append(val[0]+".city")
                    self.colsToSearch.append(val[0]+".state")
                    self.colsToSearch.append(val[0]+".country")
                else:
                    self.colsToSearch.append(val[0]+"."+val[1])
                self.fieldTables.append(val[0])

    def updateTablesToSearch(self):
        for key in self.postVar.keys():
            key = key.encode('ascii')
            pv = self.postVar[key].encode('ascii')
            if '_' in key:
                key = key.replace('_','-')
            if (pv == '') or (key == 'email') or (key == 'dataformat') or (key == 'csrfmiddlewaretoken') or (key == 'datatype'):
                pass
            else:
                if self.isField(key):
                    parts = key.split('-')
                    parts.remove('f')
                    newKey = '-'.join(parts)
                    self.fieldTables.append(ALL_POSTVARMAPS[self.datatype][newKey][0])
                else:
                    newKey = key
                self.tablesToSearch.append(ALL_POSTVARMAPS[self.datatype][newKey][0])

    def updateColsFilters(self):
        keys = self.postVar.keys()
        keys.sort()
        for key in keys:
            key = key.encode('ascii')
            pv = self.postVar[key].encode('ascii')
            if '_' in key:
                key = key.replace('_','-')
            if (pv == '') or (key == 'email') or (key == 'dataformat') or (key == 'csrfmiddlewaretoken') or self.isField(key) or (key == 'datatype'):
                self.colsFilters.append('')
            elif self.isLoc(key) or self.isDate(key):
                prefix = key.split('-')[0]
                suffix = key.split('-')[1]
                if self.isDate(key):
                    self.processDateInput(key, pv)
                    typeWanted = self.getTypeWanted(key)
                    self.colsFilters.append(self.getDateFilter(typeWanted, ALL_POSTVARMAPS[self.datatype][key][0], ALL_POSTVARMAPS[self.datatype][key][1]))
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
                if not ALL_POSTVARMAPS[self.datatype][key]:
                    print "Error, case for col=", key, " not handled!"
                else:
                    comparator = self.getComparator(key)
                    val = ALL_POSTVARMAPS[self.datatype][key]
                    self.filterTables.append(val[0])
                    if comparator == " LIKE ":
                        if key == 'pri-id' and pv.contains(','):
                            pv.replace(' ', '')
                            allpv = pv.split('-')
                            toAppend = '('
                            allpvcounter = 0
                            for value in allpv:
                                if allpvcounter < len(allpv) - 1:
                                    toAppend += "("+val[0]+"."+val[1]+comparator+"'%"+value+"%'"+") OR "
                                else:
                                    toAppend += "("+val[0]+"."+val[1]+comparator+"'%"+value+"%'"+")"
                            toAppend += ")"
                            self.colsFilters.append(toAppend)
                        else:
                            self.colsFilters.append("("+val[0]+"."+val[1]+comparator+"'%"+pv+"%'"+")")
                    else:
                        if key == 'pri-id' and pv.contains(','):
                            pv.replace(' ', '')
                            allpv = pv.split('-')
                            toAppend = '('
                            allpvcounter = 0
                            for value in allpv:
                                if allpvcounter < len(allpv) - 1:
                                    toAppend += "("+val[0]+"."+val[1]+comparator+value+") OR "
                                else:
                                    toAppend += "("+val[0]+"."+val[1]+comparator+value+")"
                            toAppend += ")"
                            self.colsFilters.append(toAppend)
                        else:
                            self.colsFilters.append("("+val[0]+"."+val[1]+comparator+pv+" )")
        for key in self.haveDate.keys():
            if self.haveDate[key]['count'] == 1:
                newKey = self.getNewDateKey(key)
                self.colsFilters.append(self.getDateFilter(key, ALL_POSTVARMAPS[self.datatype][newKey][0], ALL_POSTVARMAPS[self.datatype][newKey][1], True))
        if (self.haveDate['file']['count'] == 0) and (self.haveDate['grant']['count'] == 0):
            newKey = self.getNewDateKey('grant')
            self.colsFilters.append(self.getDateFilter('grant', ALL_POSTVARMAPS[self.datatype][newKey][0], ALL_POSTVARMAPS[self.datatype][newKey][1], True))

    def updateJoins(self):
        fdt = list(set(self.fieldTables))
        ftt = list(set(self.filterTables))
        for t in ftt:
            fdt.append(t)
        pairs = []
        i = 0
        for t in fdt:
            if i < len(fdt) - 1:
                pairs.append([fdt[i],fdt[i+1]])
            i += 1
        if self.datatype == 'raw':
            self.updateRawJoins(pairs)
        else:
            self.updateDisJoins(pairs)

    def updateDisJoins(self, pairs):
        for p in pairs:
            p0 = p[0]
            p1 = p[1]
            if ((p0,p1) in JOINS_DIS.keys()):                
                val = JOINS_DIS[(p0,p1)]
                self.tablesToSearch.append(val)
                self.colsFilters.append("("+val+"."+p0+"_id"+" = "+p0+".id)")
                self.colsFilters.append("("+val+"."+p1+"_id"+" = "+p1+".id)")
            if ((p1,p0) in JOINS_DIS.keys()):
                val = JOINS_DIS[(p1,p0)]
                self.tablesToSearch.append(val)
                self.colsFilters.append("("+val+"."+p0+"_id"+" = "+p0+".id)")
                self.colsFilters.append("("+val+"."+p1+"_id"+" = "+p1+".id)")

    def updateRawJoins(self, pairs):
        for p in pairs:
            p0 = p[0]
            p1 = p[1]
            if (p0,p1) in JOINS.keys():                
                val = JOINS[(p0,p1)]
                self.colsFilters.append("("+p0+"."+val[0]+" = "+p1+"."+val[1]+")")
            if (p1,p0) in JOINS.keys():
                val = JOINS[(p1,p0)]
                self.colsFilters.append("("+p1+"."+val[0]+" = "+p0+"."+val[1]+")")
