from api import models
import database


PLUGIN_SHOPIFY = 'easy_store'

class CampaignProduct:
    
    @staticmethod
    def get_internal_external_map(campaign):
        return { str(product.id): product.meta.get(PLUGIN_SHOPIFY,{}).get('variant_id') for product in campaign.products.all() if product.meta.get(PLUGIN_SHOPIFY,{}).get('variant_id')}
    
    @staticmethod
    def get_external_internal_map(campaign):
        return { product.meta.get(PLUGIN_SHOPIFY,{}).get('variant_id'): product.id for product in campaign.products.all() if product.meta.get(PLUGIN_SHOPIFY,{}).get('variant_id')}