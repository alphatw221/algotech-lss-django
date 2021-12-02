from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct
from api.models.cart.cart_product import CartProduct


def create_cart_product(campaign: Campaign,
                        campaign_product: CampaignProduct,
                        campaign_comment: CampaignComment,
                        qty: int, order_code: str,
                        platform: str, customer_id: str, customer_name: str,
                        remark: str, meta: dict,
                        type: str, status: str):
    try:
        return CartProduct.objects.create(
            campaign=campaign,
            campaign_product=campaign_product,
            campaign_comment=campaign_comment,
            qty=qty, order_code=order_code,
            platform=platform, customer_id=customer_id, customer_name=customer_name,
            remark=remark, meta=meta,
            type=type, status=status)
    except Exception:
        ...


def update_or_create_cart_product(campaign: Campaign,
                                  campaign_product: CampaignProduct,
                                  campaign_comment: CampaignComment,
                                  defaults: dict):
    try:
        return CartProduct.objects.update_or_create(
            campaign=campaign,
            campaign_product=campaign_product,
            campaign_comment=campaign_comment,
            defaults=defaults)
    except Exception:
        ...


def filter_last_cart_product(campaign: Campaign,
                             campaign_product: CampaignProduct,
                             type: tuple, status: str,
                             customer_id: str):
    try:
        return CartProduct.objects.filter(
            campaign=campaign,
            campaign_product=campaign_product,
            type__in=type,
            status=status,
            customer_id=customer_id).last()
    except Exception:
        ...


def update_cart_product_qty(cart_product: CartProduct, qty: int):
    try:
        cart_product.qty = qty
        cart_product.save()
    except Exception:
        ...


def filter_cart_products(campaign: Campaign,
                         campaign_product: CampaignProduct,
                         type: tuple, status: tuple) -> list[CartProduct]:
    try:
        return CartProduct.objects.filter(
            campaign=campaign,
            campaign_product=campaign_product,
            type__in=type,
            status__in=status).all()
    except Exception:
        ...
