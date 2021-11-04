from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign_product import CampaignProduct, CampaignProductSerializer


class CampaignProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignProduct.objects.all().order_by('id')
    serializer_class = CampaignProductSerializer
    filterset_fields = []
