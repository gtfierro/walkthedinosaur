#!/usr/bin/env python
"""
Using the configuration options from config.py, creates the engine and handles
creating connections to the database
"""

import config
from sqlalchemy import create_engine

def get_engine(configfile='config.ini'):
    options = config.get_config(configfile)
    if options['type'] == 'sqlite3':
        engine = create_engine('sqlite:///{db}'.format(**options))
    return engine

engine = get_engine()
 
def connect(func):
    """
    Decorator function that gives a connection to the function and closes it
    afterwards.
    [func] is the input function, which *must* accept a database connection object
    as its first argument.

    Sample usage:

    @connect
    def select_all(connection, tablename):
        return connection.execute('select * from {0}'.format(tablename))
    print select_all('mytable')
    """
    def inner(*args, **kwargs):
        conn = engine.connect()
        result = func(conn, *args, **kwargs)
        conn.close()
        return result
    return inner
