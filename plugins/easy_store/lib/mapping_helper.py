from api import models
import database


PLUGIN_EASY_STORE = 'easy_store'

class CampaignProduct:
    
    @staticmethod
    def get_internal_external_map(campaign):

        success, data, lock = database.lss_cache.campaign_product.leash_get_internal_external_map(campaign.id, PLUGIN_EASY_STORE)
        if not success and lock :
            with lock:
                data = { str(product.id):product.meta.get(PLUGIN_EASY_STORE,{}).get('variant_id') for product in campaign.products.all() if product.meta.get(PLUGIN_EASY_STORE,{}).get('variant_id')}
                database.lss_cache.campaign_product.set_external_internal_map(campaign.id, PLUGIN_EASY_STORE, data)
        elif not success:
            data = { str(product.id):product.meta.get(PLUGIN_EASY_STORE,{}).get('variant_id') for product in campaign.products.all() if product.meta.get(PLUGIN_EASY_STORE,{}).get('variant_id')}
        return data
    
    @staticmethod
    def get_external_internal_map(campaign):
        return { product.meta.get(PLUGIN_EASY_STORE,{}).get('variant_id'):product.id for product in campaign.products.all() if product.meta.get(PLUGIN_EASY_STORE,{}).get('variant_id')}