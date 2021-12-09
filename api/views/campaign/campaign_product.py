from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from api.models.campaign.campaign_product import CampaignProduct, CampaignProductSerializer, CampaignProductSerializerUpdate
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models.campaign.campaign_product import CampaignProductSerializer

import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError


def verify_request(api_user, platform_name, platform_id, campaign_id, campaign_product_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)

    if campaign_product_id:
        if not campaign.products.filter(id=campaign_product_id).exists():
            raise ApiVerifyError('no campaign product found')
        campaign_product = campaign.products.get(id=campaign_product_id)
        return platform, campaign, campaign_product

    return platform, campaign


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


class CampaignProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignProduct.objects.all().order_by('id')
    serializer_class = CampaignProductSerializer
    filterset_fields = []
    pagination_class = CampaignProductPagination

    @action(detail=True, methods=['GET'], url_path=r'retrieve_campaign_product')
    def retrieve_campaign_product(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, campaign_product = verify_request(
                api_user, platform_name, platform_id, campaign_id, campaign_product_id=pk)

            serializer = self.get_serializer(campaign_product)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_campaign_product')
    def list_campaign_product(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            order_by = request.query_params.get('order_by')
            product_status = request.query_params.get('status')
            type = request.query_params.get('type')
            key_word = request.query_params.get('key_word')
            api_user = request.user.api_users.get(type='user')
            _, campaign = verify_request(
                api_user, platform_name, platform_id, campaign_id)

            campaign_products = campaign.products.all()

            if product_status:
                campaign_products = campaign_products.filter(
                    status=product_status)
            if type:
                campaign_products = campaign_products.filter(
                    type=type)
            if key_word:
                campaign_products = campaign_products.filter(
                    name__icontains=key_word)
            if order_by:
                campaign_products = campaign_products.order_by(order_by)

            page = self.paginate_queryset(campaign_products)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data
            else:
                serializer = self.get_serializer(campaign_products, many=True)
                data = serializer.data
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "query error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_campaign_product')
    def create_campaign_product(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, campaign = verify_request(
                api_user, platform_name, platform_id, campaign_id)

            data = request.data
            data['campaign'] = campaign.id
            data['created_by'] = api_user.id
            serializer = self.get_serializer(data=data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during creating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update_campaign_product')
    def update_campaign_product(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, campaign_product = verify_request(
                api_user, platform_name, platform_id, campaign_id, campaign_product_id=pk)

            serializer = CampaignProductSerializerUpdate(
                campaign_product, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during updating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete_campaign_product')
    def delete_campaign_product(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, campaign_product = verify_request(
                api_user, platform_name, platform_id, campaign_id, campaign_product_id=pk)

            campaign_product.delete()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during deleting"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)
