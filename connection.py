#!/usr/bin/env python
"""
Using the configuration options from config.py, creates the engine and handles
creating connections to the database
"""

import config
from sqlalchemy import create_engine, MetaData, Table, inspect

def get_engine(configfile='config.ini'):
    """
    Uses configuration options in [configfile] to initialize an engine to generate
    connections to the database
    """
    options = config.get_config(configfile)
    if options['type'] == 'sqlite':
        engine = create_engine('sqlite:///{db}'.format(**options), echo=True)
    return engine

engine = get_engine()
metadata = MetaData(engine)
# allows SQLAlchemy to access preexisting tables
info = inspect(engine)
tables = {} # list of tablenames in database
for tablename in info.get_table_names():
    tables[tablename] = Table(tablename, metadata, autoload=True)
