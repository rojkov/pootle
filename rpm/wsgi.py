import os, sys
sys.path.append('/usr/lib/python2.7/site-packages/pootle/apps')
os.environ['DJANGO_SETTINGS_MODULE'] = 'pootle.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
