import os, django, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'lss.settings_social_lab'  # for rq_job
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()