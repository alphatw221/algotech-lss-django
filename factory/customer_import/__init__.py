from . import default, shc

product_import_processor_class_map = {"617":shc.SHCCustomerImportProcessor}


def get_user_import_processor_class(user_subscription=None, user_subscription_id=None):
    # return product_import_processor_class_map.get(str(user_subscription.id),default.DefaultCustomerImportProcessor)
    return shc.SHCCustomerImportProcessor