from rest_framework.permissions import BasePermission
from api.utils.common.verify import Verify

class IsPreOrderCustomer(BasePermission):

    def has_permission(self, request, view):
        try:
            pk = view.kwargs.get('pk')
            api_user = Verify.get_customer_user(request)
            pre_order = Verify.get_pre_order(pk)
            Verify.user_match_pre_order(api_user, pre_order)
        except Exception:
            return False
        return True