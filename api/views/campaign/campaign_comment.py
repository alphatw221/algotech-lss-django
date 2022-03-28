
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


    @action(detail=False, methods=['GET'], url_path=r'summarize', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def comment_category_summarize(self, request):

        api_user, campaign_id = getparams(request, ('campaign_id',),with_user=True, seller=True)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        ret = {}
        ret['total'] = db.api_campaign_comment.find({"campaign_id":campaign_id}).count()
        categories = ['delivery', 'payment']
        for category in categories:
            ret[category] = db.api_campaign_comment.find({"campaign_id":campaign_id,"categories":{"$elemMatch":category}}).count()
        
        return Response(ret, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'category_list', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def comment_category_list(self, request):

        api_user, campaign_id, category_name = getparams(request, ('campaign_id','category_name'),with_user=True, seller=True)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        
        comments = db.api_campaign_comment.find({"campaign_id":campaign_id,"categories":{"$elemMatch":category_name}})
        comments_str = dumps(comments)
        comments_json = loads(comments_str)
        return Response(comments_json, status=status.HTTP_200_OK)




