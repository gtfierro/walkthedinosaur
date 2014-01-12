import os
import sys

sys.path.append('/home/ubuntu/patent/walkthedinosaur')

os.environ['DJANGO_SETTINGS_MODULE'] = 'walkthedinosaur.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
