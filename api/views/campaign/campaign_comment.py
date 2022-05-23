from email import message
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import getdata,getparams
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler

from api.models.campaign.campaign_comment import CampaignComment, CampaignCommentSerializer, CampaignCommentSerializerTest
from api import models

import lib
from django.core import serializers
from bson.json_util import loads, dumps

class CampaignCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignComment.objects.all().order_by('id')
    serializer_class = CampaignCommentSerializer
    filterset_fields = []

    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_comment_main_categories(self, request, campaign_id):

        since, count = lib.util.getter.getparams(
            request, ('since', 'count',), with_user=False)
        
        if not since:
            since =1 

        if not count:
            count = 20

        comments = models.campaign.campaign_comment.CampaignComment.objects.filter(campaign=campaign_id).all()
        
        main_categories = serializers.serialize("json", comments.all(), fields=("id","categories", "message", "main_categories"))
        res = loads(main_categories)

        # main_categories = CampaignCommentSerializerTest(comments.all(),many=True)
        # print(main_categories)
        # res = main_categories.data

        return Response(res, status=status.HTTP_200_OK)
    



