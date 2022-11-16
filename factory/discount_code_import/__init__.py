from . import default, shc

discount_code_import_processor_class_map = {}


def get_discount_code_import_processor_class(user_subscription):
    return default.DefaultDiscountCodeImportProcessor