"""
WSGI config for lss project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
#------add thoes line if server with apache--------
import sys
sys.path.append('/home/lss_env/lib/python3.9/site-packages')
#--------------------------------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lss.settings')

application = get_wsgi_application()
