from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.auto_response.auto_response import AutoResponse, AutoResponseSerializer, AutoResponseSerializerUpdate, AutoResponseSerializerWithFacebookInfo
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel

from api.utils.common.verify import Verify
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler


class AutoResponseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = AutoResponse.objects.all().order_by('id')
    serializer_class = AutoResponseSerializer
    filterset_fields = []

    platform_dict = {'facebook': FacebookPage,
                     'youtube': YoutubeChannel}

    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def retrieve_auto_response(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        auto_response = Verify.get_auto_response_from_user_subscription(user_subscription, pk)

        return Response(AutoResponseSerializer(auto_response).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_auto_response(self, request):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        auto_responses = user_subscription.auto_responses.all()

        return Response(AutoResponseSerializerWithFacebookInfo(auto_responses, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create/(?P<platform_name>[^/.]+)/(?P<platform_id>[^/.]+)', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def create_auto_response(self, request, platform_name, platform_id):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        platform = Verify.get_platform_from_user_subscription(user_subscription, platform_name, platform_id)

        data = request.data
        data['input_msg'] = data['input_msg'].lower()
        data['user_subscription'] = user_subscription.id

        if platform_name == 'facebook':
            data['facebook_page'] = platform.id
        elif platform_name == 'youtube':
            data['youtube_channel'] = platform.id
        elif platform_name == 'instagram':
            data['instagram_profile'] = platform.id

        serializer = AutoResponseSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.save()
        
        return Response(AutoResponseSerializerWithFacebookInfo(obj).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_auto_response(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        auto_response = Verify.get_auto_response_from_user_subscription(user_subscription, pk)

        data = request.data
        data['input_msg'] = data['input_msg'].lower()
        
        serializer = AutoResponseSerializerUpdate(
            auto_response, data=data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def delete_auto_response(self, request, pk=None):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        auto_response = Verify.get_auto_response_from_user_subscription(user_subscription, pk)

        auto_response.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

