from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from ..models.campaign_order import CampaignOrder, CampaignOrderSerializer


class CampaignOrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignOrder.objects.all().order_by('id')
    serializer_class = CampaignOrderSerializer
    filterset_fields = []
