from api.models.cart.cart_product import CartProduct
from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.campaign.campaign_comment import CampaignComment


def update_or_create_cart_product(campaign: Campaign,
                                  campaign_product: CampaignProduct,
                                  campaign_comment: CampaignComment,
                                  defaults: dict):
    try:
        CartProduct.objects.update_or_create(
            campaign=campaign,
            campaign_product=campaign_product,
            campaign_comment=campaign_comment,
            defaults=defaults)
    except Exception:
        ...
