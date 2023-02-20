from . import default, shc

campaign_product_import_processor_class_map = {'617':shc.SHCProductImportProcessor}


def get_campaign_product_import_processor_class(user_subscription):
    return campaign_product_import_processor_class_map.get(str(user_subscription.id), default.DefaultCampaignProductImportProcessor)
