from rest_framework.permissions import BasePermission
from api.utils.common.verify import Verify
from api.utils.common.common import getparams


class IsPreOrderSeller(BasePermission):

    def has_permission(self, request, view):
        try:
            pk = view.kwargs.get('pk')
            api_user, platform_id, platform_name = getparams(request, ('platform_id', 'platform_name', 'order_product_id', 'qty'), with_user=True, seller=True)

            platform = Verify.get_platform(api_user, platform_name, platform_id)
            pre_order = Verify.get_pre_order(pk)
            Verify.get_campaign_from_platform(platform, pre_order.campaign.id)
            
        except Exception:
            return False
        return True


class IsCampaignPreOrderListable(BasePermission):

    def has_permission(self, request, view):
        try:
            api_user, platform_id, platform_name, campaign_id = getparams(request, ('platform_id', 'platform_name', 'campaign_id'), seller=True)

            platform = Verify.get_platform(api_user, platform_name, platform_id)
            Verify.get_campaign_from_platform(platform, campaign_id)
            
        except Exception:
            return False
        return True