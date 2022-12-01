import os
import config
import django

try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception as e:
    pass


import traceback
import service
import factory
import lib

def customer_import_job(room_id, user_subscription_id, file):
    try:
        user_subscription = lib.util.verify.Verify.get_user_subscription(user_subscription_id)
        customer_import_processor_class:factory.customer_import.default.DefaultCustomerImportProcessor \
            = factory.customer_import.get_user_import_processor_class(user_subscription)
        customer_import_processor = customer_import_processor_class(user_subscription)
        customer_import_processor.process(file)
        service.channels.data_import.send_result_data(room_id,{'result':'complete'})
    except Exception:
        print(traceback.format_exc())
        service.channels.data_import.send_result_data(room_id,{'result':'fail'})


