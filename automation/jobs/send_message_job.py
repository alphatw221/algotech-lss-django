import os
import config
import django

try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS  # for rq_job
    django.setup()
except Exception:
    pass

import service
import lib

def send_facebook_message(token, comment_id, message):
    code, ret = service.facebook.post.post_page_message_on_comment(token, comment_id, message)
    if code !=200:
        lib.util.google_cloud_logging.ApiLogEntry.write_entry(f'{comment_id}, {message}, {str(ret)}')
