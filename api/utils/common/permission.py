from rest_framework.permissions import BasePermission

from api.utils.common.verify import Verify, getparams


class PlatfomrIsCampaignOwner(BasePermission):
    def has_permission(self, request, view):
        try:
            api_user, platform_name, platform_id = getparams(request, ("platform_name", "platform_id"), with_user=True, seller=True)
            platform = Verify.get_platform(api_user, platform_name, platform_id)
            Verify.is_admin(api_user, platform_name, platform)
            return True
        except:
            return False