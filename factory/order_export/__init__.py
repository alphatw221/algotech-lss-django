from . import default, shc, kol




order_export_processor_class_map = {"617":shc.SHCOrderExportProcessor} #temp

def get_order_export_processor_class(user_subscription):
    return order_export_processor_class_map.get(str(user_subscription.id), default.DefaultOrderExportProcessor)



