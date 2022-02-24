from rest_framework.permissions import BasePermission
from api.utils.common.verify import Verify

class IsOrderCustomer(BasePermission):

    def has_permission(self, request, view):
        try:
            pk = view.kwargs.get('pk')
            api_user = Verify.get_customer_user(request)
            order = Verify.get_order(pk)

            return order.buyer == api_user
        except Exception:
            return False