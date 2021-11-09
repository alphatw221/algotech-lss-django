
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.models.campaign.campaign_comment import CampaignComment, CampaignCommentSerializer


class CampaignCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignComment.objects.all().order_by('id')
    serializer_class = CampaignCommentSerializer
    filterset_fields = []
