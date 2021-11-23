from api.models.campaign.campaign_product import CampaignProduct
from django.db import transaction


class InsufficientInventoryError(Exception):
    """Adding qty exceeds Qty sold and Qty for sale."""


class NegativeQtyError(Exception):
    """Passing in negative qty."""


class CampaignProductManager:
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

    @staticmethod
    def _check_inv(campaign_product: CampaignProduct, qty: int):
        if campaign_product.qty_sold + qty > campaign_product.qty_for_sale:
            raise InsufficientInventoryError()

    @staticmethod
    def update_status():
        ...
        # TODO: activate and deactivate campaign product
