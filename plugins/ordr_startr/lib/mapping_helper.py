from api.models.campaign.campaign import Campaign
import database
from api import models
from database.lss import campaign

PLUGIN_ORDR_STARTR = 'ordr_startr'


class CampaignProduct:
    @staticmethod
    def get_internal_external_map(campaign):
        return {str(product.id):{'id':product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id'),'order_code':product.order_code} for product in  campaign.products.all() if product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id')}

    def get_external_internal_map(campaign):


        # "name":campaign_product.name,
        #     "image":campaign_product.image,
        #     "price":float(item.get('price')),
        #     "type":campaign_product.type,

        return {product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id'):{
            'id':product.id,
            'name':product.name,
            'image':product.image,
            'type':product.type
            } 
            for product in  campaign.products.all() if product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id')}


