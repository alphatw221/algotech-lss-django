import os
import config
import django
import database

from lib.helper.lucky_draw_helper import FacebookSharedListCrawler
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception:
    pass

import lib

from datetime import datetime
import traceback


@lib.error_handle.error_handler.crawler_job_error_handler.crawler_job_error_handler
def crawler_shared_post_job(lucky_draw_id, facebook_page_username, post_id):
    print("start crawler")
    lucky_draw = database.lss.lucky_draw.CampaignLuckyDraw.get_object(id = lucky_draw_id)
    fb_crawler = FacebookSharedListCrawler(facebook_page_username, post_id)
    shared_user_name_set = fb_crawler.start()
    meta = lucky_draw['meta']
    meta["shared_post_data"] = list(shared_user_name_set)
    print(meta)
    database.lss.lucky_draw.CampaignLuckyDraw.update(meta=meta)