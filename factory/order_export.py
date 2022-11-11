from django.http import HttpResponse

from api import models
import lib
       
class OrderExportProcessor:

    def __init__(self, user_subscription, **kwargs) -> None:
        self.user_subscription = user_subscription
        self.query_params = kwargs

    def export_order_data(self):

        if self.query_params.get('campaign_id'):
            return [{'name':'test','role':'test'}]
        else:
            return [{'name':'test','role':'test'}]

class SHCOrderExportProcessor(OrderExportProcessor):
    pass

order_export_processor_class_map = {"617":SHCOrderExportProcessor}

def get_order_export_processor_class(user_subscription):
    return order_export_processor_class_map.get(str(user_subscription.id), OrderExportProcessor)



