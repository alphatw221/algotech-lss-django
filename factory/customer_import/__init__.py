from . import default, shc

product_import_processor_class_map = {}


def get_user_import_processor_class(user_subscription):
    return default.DefaultCustomerImportProcessor