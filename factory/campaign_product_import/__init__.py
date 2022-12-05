from . import default, shc

campaign_product_import_processor_class_map = {}


def get_campaign_product_import_processor_class(user_subscription):
    return default.DefaultCampaignProductImportProcessor