from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.auto_response.auto_response import AutoResponse, AutoResponseSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel

from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import *


def verify_request(api_user, platform_name, platform_id, auto_response_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    user_subscription = Verify.get_user_subscription(platform)
    if auto_response_id:
        if not platform.auto_responses.filter(id=auto_response_id).exists():
            raise ApiVerifyError('no auto_response found')
        auto_response = platform.auto_responses.get(id=auto_response_id)
        return platform, user_subscription, auto_response
    return platform, user_subscription


class AutoResponseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = AutoResponse.objects.all().order_by('id')
    serializer_class = AutoResponseSerializer
    filterset_fields = []

    platform_dict = {'facebook': FacebookPage,
                     'youtube': YoutubeChannel}

    @action(detail=True, methods=['GET'], url_path=r'retrieve_auto_response')
    @api_error_handler
    def retrieve_auto_response(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, _, auto_response = verify_request(
            api_user, platform_name, platform_id, auto_response_id=pk)

        serializer = self.get_serializer(auto_response)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_auto_response')
    @api_error_handler
    def list_auto_response(self, request):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        platform, _ = verify_request(
            api_user, platform_name, platform_id)

        auto_responses = platform.auto_responses.all()
        serializer = self.get_serializer(auto_responses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_auto_response')
    @api_error_handler
    def create_auto_response(self, request):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        platform, _ = verify_request(
            api_user, platform_name, platform_id)

        data = request.data
        if platform_name == 'facebook':
            data['facebook_page'] = platform.id
        elif platform_name == 'youtube':
            data['youtube'] = platform.id
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update_auto_response')
    @api_error_handler
    def update_auto_response(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, _, auto_response = verify_request(
            api_user, platform_name, platform_id, auto_response_id=pk)

        serializer = self.get_serializer(
            auto_response, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete_auto_response')
    @api_error_handler
    def delete_auto_response(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, _, auto_response = verify_request(
            api_user, platform_name, platform_id, auto_response_id=pk)

        auto_response.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)
