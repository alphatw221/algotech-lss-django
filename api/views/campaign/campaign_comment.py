
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from api.models.campaign.campaign_comment import CampaignComment, CampaignCommentSerializer
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.error_handle.error.api_error import ApiVerifyError
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.common import getdata,getparams
from backend.pymongo.mongodb import db
from rest_framework.response import Response
from bson.json_util import loads, dumps

class CampaignCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignComment.objects.all().order_by('id')
    serializer_class = CampaignCommentSerializer
    filterset_fields = []


    


    




