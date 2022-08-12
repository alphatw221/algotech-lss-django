import os
import config
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception as e:
    pass


from plugins.easy_store import service as easy_store_service

def export_product_job(user_subscription_id, credential):
    print('i am exporting product..')

    easy_store_service.channels.export_product.send_result_data(user_subscription_id,{'result':'complete'})
