from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct


def get_campaign_products(campaign: Campaign, status: int = None,
                          order_by: str = 'pk'):
    try:
        campaign_products = CampaignProduct.objects.filter(campaign=campaign)
        if status is not None:
            campaign_products = campaign_products.filter(status=status)

        return campaign_products.order_by(order_by).all()
    except Exception:
        return []


def get_campaign_products_order_codes_mapping(campaign: Campaign, status: int = None,
                                              lower: bool = True):
    try:
        campaign_products = CampaignProduct.objects.filter(campaign=campaign)
        if status is not None:
            campaign_products = campaign_products.filter(status=status)

        return {campaign_product.order_code.lower() if lower
                else campaign_product.order_code: campaign_product
                for campaign_product in campaign_products}
    except Exception:
        return []
