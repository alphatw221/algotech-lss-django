from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models.order.pre_order import PreOrder, PreOrderSerializer
from api.models.order.order import Order, OrderSerializer

from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from rest_framework.pagination import PageNumberPagination
from django.db import transaction


def verify_request(api_user, platform_name, platform_id, campaign_id, pre_order_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)

    if pre_order_id:
        if not campaign.pre_orders.filter(id=pre_order_id).exists():
            raise ApiVerifyError('no campaign product found')
        pre_order = campaign.pre_orders.get(id=pre_order_id)
        return platform, campaign, pre_order

    return platform, campaign


class PreOrderPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = PreOrder.objects.all().order_by('id')
    serializer_class = PreOrderSerializer
    filterset_fields = []

    @action(detail=True, methods=['GET'], url_path=r'retrieve')
    def retrieve_pre_order(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, pre_order = verify_request(
                api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

            serializer = PreOrderSerializer(pre_order)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list')
    def list_pre_order(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, campaign = verify_request(
                api_user, platform_name, platform_id, campaign_id)

            queryset = campaign.pre_orders.all()

            # TODO filtering
            page = PreOrderPagination.paginate_queryset(queryset)
            if page is not None:
                serializer = PreOrderSerializer(page, many=True)
                result = PreOrderPagination.get_paginated_response(
                    serializer.data)
                data = result.data
            else:
                serializer = PreOrderSerializer(queryset, many=True)
                data = serializer.data

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "query error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'checkout')
    def pre_order_checkout(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, pre_order = verify_request(
                api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

            with transaction.atomic():
                serializer = OrderSerializer(
                    data=PreOrderSerializer(pre_order).data)
                if not serializer.is_valid():
                    pass
                order = serializer.save()

                # TODO empty pre_order table
                # TODO
                # order.delievery=request.data

                for order_product in pre_order.order_products.all():
                    order_product.pre_order = None
                    order_product.order = order.id
                    order_product.save()
                serializer = OrderSerializer(order)

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)


# add order_product


# update order_product


# delete order_product
