from rest_framework.permissions import BasePermission

# class IsAuthenticated(BasePermission):
#     """
#     Allows access only to authenticated users.
#     """

#     def has_permission(self, request, view):

#         print(type(request.user))
#         print((request.user))
#         return bool(request.user)

class IsAuthorizedByUserSubscription(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):

        user_subscription_id = view.kwargs.get('user_subscription_id')

        # if not isinstance(request.user,'')
        developer = request.user

        if user_subscription_id not in developer.authorization.get('user_subscription',{}):
            return False
        
        return True

