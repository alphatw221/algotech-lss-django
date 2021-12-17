from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models.order.order import Order, OrderSerializer, OrderSerializerUpdatePayment, OrderSerializerUpdateShipping
import json

from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from rest_framework.pagination import PageNumberPagination
from django.db import transaction


def verify_buyer_request(api_user, order_id):
    if not api_user:
        raise ApiVerifyError("no user found")
    elif api_user.status != "valid":
        raise ApiVerifyError("not activated user")
    if not api_user.order.filter(id=order_id).exists():
        raise ApiVerifyError("not pre_order found")
    return api_user.order.get(id=order_id)


def verify_seller_request(api_user, platform_name, platform_id, campaign_id, order_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)

    if order_id:
        if not campaign.order.filter(id=order_id).exists():
            raise ApiVerifyError('no campaign product found')
        order = campaign.order.get(id=order_id)
        return platform, campaign, order

    return platform, campaign


def verify_payment_delivery(api_user, order_id):
    if not api_user:
        raise ApiVerifyError("no user found")
    elif api_user.status != "valid":
        raise ApiVerifyError("not activated user")
    if not api_user.order.filter(id=order_id).exists():
        raise ApiVerifyError("not pre_order found")

    order = OrderSerializer.objects.get(id=order_id)
    if order.payment_first_name == '':
        raise ApiVerifyError("no payment first name")
    if order.payment_last_name == '':
        raise ApiVerifyError("no payment last name")
    if order.payment_company == '':
        raise ApiVerifyError("no payment company")
    if order.payment_postcode == '':
        raise ApiVerifyError("no payment post code")
    if order.payment_region == '':
        raise ApiVerifyError("no payment region")
    if order.payment_location == '':
        raise ApiVerifyError("no payment location")
    if order.payment_address_1 == '':
        raise ApiVerifyError("no payment address")
    if order.payment_method == '':
        raise ApiVerifyError("no payment location")
    if order.payment_location == '':
        raise ApiVerifyError("no payment location")
    return api_user.order.get(id=order_id)


class OrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all().order_by('id')
    serializer_class = OrderSerializer
    filterset_fields = []

    @action(detail=True, methods=['GET'], url_path=r'buyer_retrieve')
    def buyer_retrieve_order(self, request, pk=None):
        try:
            api_user = request.user.api_users.get(type='customer')

            order = verify_buyer_request(
                api_user, order_id=pk)

            serializer = OrderSerializer(order)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'seller_retrieve')
    def seller_retrieve_order(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, order = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id, order_id=pk)

            serializer = OrderSerializer(order)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'seller_list')
    def seller_list_order(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')
            order_by = request.query_params.get('order_by')

            _, campaign = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id)

            queryset = campaign.order.all()
            # TODO filtering
            if order_by:
                queryset = queryset.order_by(order_by)
            
            page = OrderPagination.paginate_queryset(queryset)
            if page is not None:
                serializer = OrderSerializer(page, many=True)
                result = OrderPagination.get_paginated_response(
                    serializer.data)
                data = result.data
            else:
                serializer = OrderSerializer(queryset, many=True)
                data = serializer.data

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "query error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'buyer_info')
    def seller_pre_order_checkout(self, request, pk=None):
        try:
            api_user = request.user.api_users.get(type='customer')

            order = verify_buyer_request(
                api_user, order_id=pk)
            
            serializer = OrderSerializer(order)
            serializer = OrderSerializerUpdatePayment(order, data=request.data, partial=True)
            if not serializer.is_valid():
                pass
            serializer = OrderSerializerUpdateShipping(order, data=request.data, partial=True)
            if not serializer.is_valid():
                pass

            order = serializer.save()

            serializer = OrderSerializer(order)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path=r'buyer_info')
    def buyer_update_delivery_payment_info(self, request, pk=None):
        try:
            api_user = request.user.api_users.get(type='customer')

            order = verify_buyer_request(
                api_user, order_id=pk)
            
            serializer = OrderSerializer(order)
            serializer = OrderSerializerUpdatePayment(order, data=request.data, partial=True)
            if not serializer.is_valid():
                pass
            serializer = OrderSerializerUpdateShipping(order, data=request.data, partial=True)
            if not serializer.is_valid():
                pass

            order = serializer.save()

            serializer = OrderSerializer(order)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'order_submit')
    def buyer_order_submit(self, request, pk=None):
        try:
            api_user = request.user.api_users.get(type='customer')

            order = verify_payment_delivery(
                api_user, order_id=pk)
            
            # update status
            order.status = 'unpaid'
            order.save()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "status update to unpaid"}, status=status.HTTP_200_OK)

        
# payment_submit
# 驗證付款info
# ...update status
# ...update payment detail

# cancel
# ...check order status staging
