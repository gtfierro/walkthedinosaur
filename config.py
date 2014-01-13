#!/usr/bin/env python
"""
Handles getting configuration options from the file
"""
from ConfigParser import ConfigParser
import os

CONFIG_PATH_PREFIX = os.path.dirname(os.path.abspath(__file__))

cfgfile = CONFIG_PATH_PREFIX + '/config.ini'

def get_config(filename=cfgfile):
    """
    Grabs configuration file and parses options.
    """
    cfg = ConfigParser()
    cfg.read(filename)
    dbtype = cfg.get('global','type')
    db = cfg.get('global', 'database')
    if (dbtye == 'sqlite'):
        db = CONFIG_PATH_PREFIX + '/' + cfg.get('global', 'database')
    dbtype = cfg.get('global', 'type')
    host = cfg.get('global', 'host')
    user = cfg.get('global', 'user')
    password = cfg.get('global', 'password')
    port = cfg.get('global', 'port')
    local = False
    if cfg.get('global', 'local') == 'yes':
        local = True
    return {'db': db,
            'type': type,
            'user': user,
            'pass': password,
            'host': host,
            'type': dbtype,
            'local': local,
            'port': port}

if __name__ == '__main__':
    print get_config()
