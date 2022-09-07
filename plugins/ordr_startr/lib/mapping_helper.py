from api.models.campaign.campaign import Campaign
import database
from api import models
from database.lss import campaign

PLUGIN_ORDR_STARTR = 'ordr_startr'


class CampaignProduct:
    @staticmethod
    def get_internal_external_map(campaign):
        return {str(product.id):product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id') for product in  campaign.products.all() if product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id')}

    def get_external_internal_map(campaign):
        return {product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id'):{"id":product.id,"order_code":product.order_code}for product in  campaign.products.all() if product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id')}


