from api.models.campaign.campaign_lucky_draw import (
    CampaignLuckyDraw, CampaignLuckyDrawSerializer)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class CampaignLuckyDrawViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignLuckyDraw.objects.all().order_by('id')
    serializer_class = CampaignLuckyDrawSerializer
    filterset_fields = []
