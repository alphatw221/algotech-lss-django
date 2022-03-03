from rest_framework.permissions import BasePermission
from api.utils.common.verify import Verify
from api.utils.common.common import getparams



class IsPlatformCampaignRetrievable(BasePermission):
    def has_permission(self, request, view):
        try:
            pk = view.kwargs.get('pk')
            api_user, platform_name, platform_id = getparams(request, ("platform_name", "platform_id"), with_user=True, seller=True)
            platform = Verify.get_platform(api_user, platform_name, platform_id)
            Verify.get_campaign_from_platform(platform, pk)
            return True
        except:
            return False

class IsCampaignPlatformValid(BasePermission):
    def has_permission(self, request, view):
        try:
            api_user, platform_name, platform_id = getparams(request, ("platform_name", "platform_id"), with_user=True, seller=True)
            Verify.get_platform(api_user, platform_name, platform_id)
            return True
        except:
            return False




