from . import default, shc

discount_code_import_processor_class_map = {"617":shc.SHCDiscountCodeImportProcessor}

def get_discount_code_import_processor_class(user_subscription):
    return discount_code_import_processor_class_map.get(str(user_subscription.id), default.DefaultDiscountCodeImportProcessor)