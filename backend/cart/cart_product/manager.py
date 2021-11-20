from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.campaign.campaign_comment import CampaignComment
from api.utils.orm.cart_product import update_or_create_cart_product


class CartProductManager:
    @staticmethod
    def update_or_create(campaign: Campaign,
                         campaign_product: CampaignProduct,
                         campaign_comment: CampaignComment,
                         qty: int, order_code: str, platform: str,
                         customer_id: str, customer_name: str,
                         type: str, status: str):
        update_or_create_cart_product(
            campaign,
            campaign_product,
            campaign_comment,
            {
                'qty': qty,
                'order_code': order_code,
                'platform': platform,
                'customer_id': customer_id,
                'customer_name': customer_name,
                'type': type,
                'status': status,
            }
        )
