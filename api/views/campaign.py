from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign import Campaign, CampaignSerializer


class CampaignViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Campaign.objects.all().order_by('id')
    serializer_class = CampaignSerializer
    filterset_fields = []
