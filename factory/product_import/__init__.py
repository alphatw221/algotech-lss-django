from . import default, shc

product_import_processor_class_map = {'617':shc.SHCProductImportProcessor}


def get_product_import_processor_class(user_subscription):
    return product_import_processor_class_map.get(str(user_subscription.id),default.DefaultProductImportProcessor)
    # return default.DefaultProductImportProcessor