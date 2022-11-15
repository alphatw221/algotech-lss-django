from . import default, shc

product_import_processor_class_map = {}


def get_product_import_processor_class(user_subscription):
    return default.DefaultProductImportProcessor