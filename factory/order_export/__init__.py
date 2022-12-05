from . import default, shc




order_export_processor_class_map = {"617":shc.SHCOrderExportProcessor}

def get_order_export_processor_class(user_subscription):
    return shc.SHCOrderExportProcessor
    return order_export_processor_class_map.get(str(user_subscription.id), default.DefaultOrderExportProcessor)



