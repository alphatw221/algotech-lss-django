from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.utils.orm import campaign_product
from django.db import transaction


class InsufficientInventoryError(Exception):
    """Adding qty exceeds Qty sold and Qty for sale."""


class NegativeQtyError(Exception):
    """Passing in negative qty."""


class AlreadyInUseError(Exception):
    """Passing in a value already in use."""


class CampaignProductManager:
    @staticmethod
    def get_campaign_products(campaign: Campaign, status: int = None,
                              order_by: str = 'pk') -> list[CampaignProduct]:
        return campaign_product.get_campaign_products(campaign, status, order_by)

    @staticmethod
    def get_order_codes_mapping(campaign: Campaign, status: int = None,
                                lower: bool = True):
        campaign_products = CampaignProductManager.get_campaign_products(
            campaign, status)

        return {campaign_product.order_code.lower() if lower
                else campaign_product.order_code: campaign_product
                for campaign_product in campaign_products}

    @staticmethod
    def update_qty_sold(campaign_product: CampaignProduct, qty: int, orig_qty: int = 0,
                        check_inv: bool = True):
        if qty < 0 or orig_qty < 0:
            raise NegativeQtyError()

        campaign_product = CampaignProduct.objects.select_for_update().get(
            pk=campaign_product.pk)
        with transaction.atomic():
            qty -= orig_qty

            if check_inv:
                CampaignProductManager._check_inv(campaign_product, qty)

            campaign_product.qty_sold += qty
            campaign_product.save()

            return campaign_product

    @staticmethod
    def update_status(campaign_product: CampaignProduct, status: int):
        if status == campaign_product.status:
            raise AlreadyInUseError()

        campaign_product = CampaignProduct.objects.select_for_update().get(
            pk=campaign_product.pk)
        with transaction.atomic():
            campaign_product.status = status
            campaign_product.save()

            return campaign_product

    @staticmethod
    def _check_inv(campaign_product: CampaignProduct, qty: int):
        if campaign_product.qty_sold + qty > campaign_product.qty_for_sale:
            raise InsufficientInventoryError()
