from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from api.models.campaign.campaign_product import CampaignProduct, CampaignProductSerializer


class CampaignProductPagination(LimitOffsetPagination):

    default_limit = 25
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100


class CampaignProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignProduct.objects.all().order_by('id')
    serializer_class = CampaignProductSerializer
    filterset_fields = []
    pagination_class = CampaignProductPagination
