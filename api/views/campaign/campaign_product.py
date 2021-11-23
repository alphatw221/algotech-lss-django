from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from api.models.campaign.campaign_product import CampaignProduct, CampaignProductSerializer


class CampaignProductPagination(PageNumberPagination):

    page_size = 25
    page_query_param = 'page'
    page_size_query_param = 'page_size'

    # django_paginator_class - The Django Paginator class to use. Default is django.core.paginator.Paginator, which should be fine for most use cases.
    # page_size - A numeric value indicating the page size. If set, this overrides the PAGE_SIZE setting. Defaults to the same value as the PAGE_SIZE settings key.
    # page_query_param - A string value indicating the name of the query parameter to use for the pagination control.
    # page_size_query_param - If set, this is a string value indicating the name of a query parameter that allows the client to set the page size on a per-request basis. Defaults to None, indicating that the client may not control the requested page size.
    # max_page_size - If set, this is a numeric value indicating the maximum allowable requested page size. This attribute is only valid if page_size_query_param is also set.
    # last_page_strings - A list or tuple of string values indicating values that may be used with the page_query_param to request the final page in the set. Defaults to ('last',)
    # template - The name of a template to use when rendering pagination controls in the browsable API. May be overridden to modify the rendering style, or set to None to disable HTML pagination controls completely. Defaults to "rest_framework/pagination/numbers.html".



class CampaignProductPagination(PageNumberPagination):

    default_limit = 25


class CampaignProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignProduct.objects.all().order_by('id')
    serializer_class = CampaignProductSerializer
    filterset_fields = []
    pagination_class = CampaignProductPagination
