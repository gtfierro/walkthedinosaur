#!/usr/bin/env python
"""
Handles getting configuration options from the file
"""
from ConfigParser import ConfigParser

def get_config(filename):
    """
    Grabs configuration file and parses options.
    """
    cfg = ConfigParser()
    cfg.read(filename)
    db = cfg.get('global', 'database')
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
