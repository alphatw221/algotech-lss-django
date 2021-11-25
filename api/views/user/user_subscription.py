from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user import User
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from datetime import datetime
from backend.api.facebook.user import api_fb_get_me_accounts


class UserSubscriptionPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


platform_dict = {'facebook': FacebookPage,
                 'youtube': YoutubeChannel}


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = UserSubscription.objects.all().order_by('id')
    serializer_class = UserSubscriptionSerializer
    filterset_fields = []
    pagination_class = UserSubscriptionPagination

    @action(detail=False, methods=['GET'], url_path=r'root_add_platform')
    def root_add_platform(self, request):

        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        user_subscription_id = request.query_params.get('user_subscription_id')

        api_user = request.user.api_users.get(type='user')
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if platform_name not in platform_dict:
            return Response({"message": "no platfrom name found"}, status=status.HTTP_400_BAD_REQUEST)

        if not platform_dict[platform_name].objects.filter(id=platform_id).exists():
            return Response({"message": "no platfrom found"}, status=status.HTTP_400_BAD_REQUEST)

        platform = platform_dict[platform_name].objects.get(
            id=platform_id)

        if not api_user.user_subscriptions.filter(id=user_subscription_id).exists():
            return Response({"message": "no user_subscription found"}, status=status.HTTP_400_BAD_REQUEST)

        user_subscription = api_user.user_subscriptions.get(
            id=user_subscription_id)

        if platform.user_subscriptions.filter(id=user_subscription.id).exists():
            return Response({"message": "platfom already in user_subscription"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if platform_name == 'facebook':
                user_subscription.facebook_pages.add(platform)
            elif platform_name == 'youtube':
                pass
        except:
            return Response({"message": "error occerd during process"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': "add platform success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'root_remove_platform')
    def root_remove_platform(self, request):

        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        user_subscription_id = request.query_params.get('user_subscription_id')

        api_user = request.user.api_users.get(type='user')
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if platform_name not in platform_dict:
            return Response({"message": "no platfrom name found"}, status=status.HTTP_400_BAD_REQUEST)

        if not platform_dict[platform_name].objects.filter(id=platform_id).exists():
            return Response({"message": "no platfrom found"}, status=status.HTTP_400_BAD_REQUEST)

        platform = platform_dict[platform_name].objects.get(
            id=platform_id)

        if not api_user.user_subscriptions.filter(id=user_subscription_id).exists():
            return Response({"message": "no user_subscription found"}, status=status.HTTP_400_BAD_REQUEST)

        user_subscription = api_user.user_subscriptions.get(
            id=user_subscription_id)

        if not platform.user_subscriptions.filter(id=user_subscription.id).exists():
            return Response({"message": "platfom not in user_subscription"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if platform_name == 'facebook':
                user_subscription.facebook_pages.remove(platform)
            elif platform_name == 'youtube':
                pass
        except:
            return Response({"message": "error occerd during process"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': "remove platform success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'root_add_user')
    def root_add_user(self, request):

        target_user_id = request.query_params.get('target_user_id')
        user_subscription_id = request.query_params.get('user_subscription_id')

        api_user = request.user.api_users.get(type='user')
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(id=target_user_id, type='user').exists():
            return Response({"message": "no target user found"}, status=status.HTTP_400_BAD_REQUEST)
        target_user = User.objects.get(id=target_user_id, type='user')
        if target_user.status != "valid":
            return Response({"message": "target user not activated"}, status=status.HTTP_400_BAD_REQUEST)

        if not api_user.user_subscriptions.filter(id=user_subscription_id).exists():
            return Response({"message": "no user_subscription found"}, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = api_user.user_subscriptions.get(
            id=user_subscription_id)

        if user_subscription.root_users.filter(id=target_user.id).exists():
            return Response({"message": "target user already in user_subscription"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_subscription.root_users.add(target_user)
        except:
            return Response({"message": "error occerd during process"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': "add target user success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'root_remove_user')
    def root_remove_user(self, request):

        target_user_id = request.query_params.get('target_user_id')
        user_subscription_id = request.query_params.get('user_subscription_id')

        api_user = request.user.api_users.get(type='user')
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(id=target_user_id, type='user').exists():
            return Response({"message": "no target user found"}, status=status.HTTP_400_BAD_REQUEST)
        target_user = User.objects.get(id=target_user_id, type='user')
        if target_user.status != "valid":
            return Response({"message": "target user not activated"}, status=status.HTTP_400_BAD_REQUEST)

        if not api_user.user_subscriptions.filter(id=user_subscription_id).exists():
            return Response({"message": "no user_subscription found"}, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = api_user.user_subscriptions.get(
            id=user_subscription_id)

        if not user_subscription.root_users.filter(id=target_user.id).exists():
            return Response({"message": "target user not in user_subscription"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_subscription.root_users.remove(target_user)
        except:
            return Response({"message": "error occerd during process"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': "delete target user success"}, status=status.HTTP_200_OK)
