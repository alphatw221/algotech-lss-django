from functools import partial
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign import Campaign, CampaignSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action

from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from backend.api.facebook.user import api_fb_get_me_accounts
platform_dict = {'facebook': FacebookPage,
                 'youtube': YoutubeChannel}


class CampaignPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CampaignViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Campaign.objects.all().order_by('id')
    serializer_class = CampaignSerializer
    filterset_fields = []
    pagination_class = CampaignPagination

    @action(detail=True, methods=['GET'], url_path=r'retrieve_campaign')
    def retrieve_campaign(self, request, pk=None):

        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
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

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        if not platform.campaigns.filter(id=pk).exists():
            return Response({"message": "no campaign found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            campaign = platform.campaigns.get(id=pk)
            serializer = self.get_serializer(campaign)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_campaign')
    def list_campaign(self, request):

        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')

        order_by = request.query_params.get('order_by')
        product_status = request.query_params.get('status')
        key_word = request.query_params.get('key_word')

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
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

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        campaigns = platform.campaigns.all()
        try:
            if product_status:
                campaigns = campaigns.filter(status=product_status)
            if key_word:
                campaigns = campaigns.filter(name__icontains=key_word)
            if order_by:
                campaigns = campaigns.order_by(order_by)
        except:
            return Response({"message": "query error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        page = self.paginate_queryset(campaigns)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(campaigns, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_campaign')
    def create_campaign(self, request):

        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
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

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = request.data
            data['created_by'] = api_user.id
            # TODO 之後要改寫
            data['facebook_page'] = platform.id if platform_name == 'facebook' else None
            data['youtube_channel'] = platform.id if platform_name == 'youtube' else None
            serializer = self.get_serializer(data=data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except:
            return Response({"message": "error occerd during creating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update_campaign')
    def update_campaign(self, request, pk=None):

        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
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

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        if not platform.campaigns.filter(id=pk).exists():
            return Response({"message": "no campaign found"}, status=status.HTTP_400_BAD_REQUEST)
        campaign = platform.campaigns.get(id=pk)

        try:
            serializer = self.get_serializer(
                campaign, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except:
            return Response({"message": "error occerd during updating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete_campaign')
    def delete_campaign(self, request, pk=None):

        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
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

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        if not platform.campaigns.filter(id=pk).exists():
            return Response({"message": "no campaign found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            platform.campaigns.get(id=pk).delete()
        except:
            return Response({"message": "error occerd during deleting"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)


def is_admin(platform_name, api_user, platform):
    try:
        if platform_name == 'facebook':
            status_code, response = api_fb_get_me_accounts(
                api_user.facebook_info['token'])

            for item in response['data']:
                if item['id'] == platform.page_id:
                    return True
            return False
        elif platform_name == 'youtube':
            pass
    except:
        return False
    return False
