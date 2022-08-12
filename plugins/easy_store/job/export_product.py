from api import models
import lib
from .. import service as easy_store_service

def export_product_job(user_subscription_id, credential):
    print('i am exporting product..')

    easy_store_service.channels.export_product.send_result_data(user_subscription_id,{'result':'complete'})
