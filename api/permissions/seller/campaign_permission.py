from rest_framework.permissions import BasePermission
from api.utils.common.verify import Verify
from api.utils.common.common import getparams



class IsCampaignSeller(BasePermission):

    def has_permission(self, request, view):
        try:
            api_user, platform_id, platform_name, campaign_id = getparams(request, ('platform_id', 'platform_name', 'campaign_id'), seller=True)

            platform = Verify.get_platform(api_user, platform_name, platform_id)
            Verify.get_campaign_from_platform(platform, campaign_id)
            
        except Exception:
            return False
        return True




class IsCampaignRetrievable(BasePermission):
    def has_permission(self, request, view):
        try:
            pk = view.kwargs.get('pk')
            api_user, platform_name, platform_id = getparams(request, ("platform_name", "platform_id"), with_user=True, seller=True)
            platform = Verify.get_platform(api_user, platform_name, platform_id)
            Verify.is_admin(api_user, platform_name, platform)
            return True
        except:
            return False
    def has_object_permission(self, request, view, obj):
        print(view)
        print(obj)



class PlatfomrIsCampaignOwner(BasePermission):
    def has_permission(self, request, view):
        print(view)
        try:

            api_user, platform_name, platform_id = getparams(request, ("platform_name", "platform_id"), with_user=True, seller=True)
            platform = Verify.get_platform(api_user, platform_name, platform_id)
            Verify.is_admin(api_user, platform_name, platform)
            return True
        except:
            return False
    def has_object_permission(self, request, view, obj):
        print(view)
        print(obj)

