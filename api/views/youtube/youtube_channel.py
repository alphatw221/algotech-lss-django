
from rest_framework import views, viewsets, status
from rest_framework import views, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import default_storage


from api.utils.common.common import getdata, getparams
from api.models.youtube.youtube_channel import YoutubeChannel

import datetime
import hashlib
from api.utils.common.verify import Verify
from backend.pymongo.mongodb import db

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.error_handle.error.api_error import ApiVerifyError
from bson.json_util import loads, dumps

class YoutubeViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()

    @action(detail=False, methods=['GET'], url_path=r'get_comment', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_youtube_comment(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id, since_timestamp, count = getparams(request, ('platform_id', "platform_name", 'campaign_id', 'since_timestamp', "count"), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        Verify.get_campaign_from_platform(platform, campaign_id)

        if not since_timestamp:
            since_timestamp =1 

        if not count:
            count = 20

        # comments = db.api_campaign_comment.find({"campaign_id":int(campaign_id),"platform":"youtube"},{'_id': False}).limit(count)

        comments = db.api_campaign_comment.find({"campaign_id":int(campaign_id),"platform":"facebook"},{'_id': False}).limit(count)

        comments_str = dumps(comments)
        comments_json = loads(comments_str)
        return Response(comments_json, status=status.HTTP_200_OK)
        