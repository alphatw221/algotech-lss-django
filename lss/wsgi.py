"""
WSGI config for lss project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""


import os
from .. import config
#------add thoes line if server with apache--------
import sys
sys.path.append(config.POETRY_ENVIRONMENT)
#--------------------------------------------------
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', config.DJANGO_SETTINGS)

application = get_wsgi_application()