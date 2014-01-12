#!/usr/bin/env python
"""
Using the configuration options from config.py, creates the engine and handles
creating connections to the database
"""

import config
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker


# Uses the file specified in config.py as default config file.
def get_engine(configfile=config.cfgfile):
    """
    Uses configuration options in [configfile] to initialize an engine to generate
    connections to the database
    """
    options = config.get_config(configfile)
    print options
    if options['type'] == 'sqlite':
        engine = create_engine('sqlite:///{db}'.format(**options), echo=True)
    elif options['type'] == 'mysql':
        engine = create_engine('mysql+mysqldb://{user}:{pass}@{host}/{db}?charset=utf8'.format(**options), echo=True)
    return engine

engine = get_engine()
metadata = MetaData(engine)
# allows SQLAlchemy to access preexisting tables
info = inspect(engine)
tables = {} # list of tablenames in database
for tablename in info.get_table_names():
    tables[tablename] = Table(tablename, metadata, autoload=True).columns

"""
Session = sessionmaker(bind=engine)
session = Session()
patent_type_query = "SELECT DISTINCT type FROM patent;"
result = session.execute(patent_type_query)
for row in result:
	patent_types.append(row['type'])
if len(patent_types) == 0:
	print "No results found"


patent_table = Table('patent', metadata, autoLoad=True)
for c in patent_table.columns:
	if c.name == "type":
		for entry in c:
			patent_types.append(entry.name)
"""
