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
    return {'db': db,
            'type': dbtype}

if __name__ == '__main__':
    print get_config()
