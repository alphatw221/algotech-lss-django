from api.models.campaign.campaign import Campaign
import database
from api import models
from database.lss import campaign

PLUGIN_ORDR_STARTR = 'ordr_startr'

def get_campaign_product_map(campaign):
    # success, data, lock = database.lss_cache.campaign_product.leash_get_campaign_products_map(campaign.id, PLUGIN_ORDR_STARTR)
    # if not success:
    #     with lock:
    #         pass
    #         data = {product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id'):product.id for product in  campaign.products.all() if product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id')}
    data = {product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id'):product.id for product in  campaign.products.all() if product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id')}

    return data 