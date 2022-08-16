
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import lib

# class TwitchViewSet(viewsets.GenericViewSet):

#     @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/bulk/create/comment', permission_classes=(IsAuthenticated,))
#     @lib.error_handle.error_handler.api_error_handler.api_error_handler
#     def check_facebook_page_token(self, request, campaign_id):
#         api_user = lib.util.verify.Verify.get_seller_user(request)
#         user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
#         campaign =  lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
#         comments, = lib.util.getter.getdata(request, ('comments', ), required=True)        

#         print (comments)

#         # if 'twitch' not in user_subscription.user_plan.get('activated_platform'):
#         #     raise lib.error_handle.error.api_error.ApiVerifyError('twitch not activated')


#         return Response('ss', status=status.HTTP_200_OK)
