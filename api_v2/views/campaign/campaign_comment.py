from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from api import models
from api.models.campaign.campaign_comment import CampaignCommentSerializer

import lib

class CampaignCommentPagination(CursorPagination):
    page_size_query_param = 'page_size'
    ordering = '-created_time'
    page_size=25
class CampaignCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.campaign.campaign_comment.CampaignComment.objects.all().order_by('id')
    pagination_class = CampaignCommentPagination

    @action(detail=True, methods=['GET'], url_path=r'summarize', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_summerize_comment_main_categories(self, request, pk):

        tag, = lib.util.getter.getparams(request, ('tag',), with_user=False)
        print(tag)
        
        comments = models.campaign.campaign_comment.CampaignComment.objects.filter(campaign=pk, categories__contains=tag.lower())
        
        main_categories = CampaignCommentSerializer(comments, many=True)
        res = main_categories.data

        return Response(res, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/(?P<platform_name>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_platform_comments(self, request, campaign_id, platform_name):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription =  lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign =  lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        category, = lib.util.getter.getparams(request, ('category',), with_user=False)

        queryset = campaign.comments.all().order_by('-created_time')
        


        if platform_name in [models.user.user_subscription.PLATFORM_FACEBOOK,
                            models.user.user_subscription.PLATFORM_YOUTUBE,
                            models.user.user_subscription.PLATFORM_INSTAGRAM,
                            models.user.user_subscription.PLATFORM_TWITCH,
                            models.user.user_subscription.PLATFORM_TIKTOK]:
            queryset = queryset.filter(platform=platform_name).order_by('-created_time')

        if category not in [None, '', 'null', 'undefined']:
            queryset = queryset.filter(categories__contains=category.lower()).order_by('-created_time')

        page = self.paginate_queryset(queryset)
        serializer = models.campaign.campaign_comment.CampaignCommentSerializer(page, many=True)

        return Response(self.get_paginated_response(serializer.data).data, status=status.HTTP_200_OK)

    
