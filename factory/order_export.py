from django.http import HttpResponse

from api import models
import lib
       
class OrderExportProcessor:

    def __init__(self, user_subscription, **kwargs) -> None:
        self.user_subscription = user_subscription
        self.query_params = kwargs

    def export_order(self):

        if self.query_params.get('campaign_id'):
            campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(self.user_subscription, self.query_params.get('campaign_id'))
            buffer = lib.helper.xlsx_helper.OrderReport.create(campaign, self.user_subscription.lang)

            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=orders.xlsx'
            return response
        else:
            pass

class SHCOrderExportProcessor(OrderExportProcessor):
    pass

order_export_processor_class_map = {"617":SHCOrderExportProcessor}

def get_order_export_processor_class(user_subscription):
    return order_export_processor_class_map.get(str(user_subscription.id), OrderExportProcessor)



