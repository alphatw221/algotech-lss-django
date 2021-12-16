from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models.order.pre_order import PreOrder, PreOrderSerializer
from api.models.order.order import Order, OrderSerializer, OrderSerializerUpdateShipping

from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import F


def verify_buyer_request(api_user, pre_order_id):
    if not api_user:
        raise ApiVerifyError("no user found")
    elif api_user.status != "valid":
        raise ApiVerifyError("not activated user")
    if not api_user.pre_orders.filter(id=pre_order_id).exists():
        raise ApiVerifyError("not pre_order found")
    return api_user.pre_orders.get(id=pre_order_id)


def verify_seller_request(api_user, platform_name, platform_id, campaign_id, pre_order_id=None):
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

    @action(detail=True, methods=['GET'], url_path=r'buyer_retrieve')
    def buyer_retrieve_pre_order(self, request, pk=None):
        try:
            api_user = request.user.api_users.get(type='customer')

            pre_order = verify_buyer_request(
                api_user, pre_order_id=pk)

            serializer = PreOrderSerializer(pre_order)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_retrieve')
    def seller_retrieve_pre_order(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, pre_order = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

            serializer = PreOrderSerializer(pre_order)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller_list')
    def seller_list_pre_order(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, campaign = verify_seller_request(
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

    @action(detail=True, methods=['POST'], url_path=r'buyer_checkout')
    def buyer_pre_order_checkout(self, request, pk=None):
        try:
            api_user = request.user.api_users.get(type='customer')

            pre_order = verify_buyer_request(
                api_user, pre_order_id=pk)

            with transaction.atomic():
                serializer = OrderSerializer(
                    data=PreOrderSerializer(pre_order).data)
                if not serializer.is_valid():
                    pass
                order = serializer.save()

                # update shipping info
                serializer = OrderSerializerUpdateShipping(order,
                                                           data=request.data, partial=True)
                if not serializer.is_valid():
                    pass
                order = serializer.save()

                for order_product in pre_order.order_products.all():
                    order_product.pre_order = None
                    order_product.order = order.id
                    order_product.save()

                # empty pre_order table
                pre_order.products = {}
                pre_order.total = 0
                pre_order.subtotal = 0
                pre_order.save()

                serializer = OrderSerializer(order)

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'seller_checkout')
    def seller_pre_order_checkout(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, pre_order = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

            with transaction.atomic():
                serializer = OrderSerializer(
                    data=PreOrderSerializer(pre_order).data)
                if not serializer.is_valid():
                    pass
                order = serializer.save()

                # update shipping info
                serializer = OrderSerializerUpdateShipping(order,
                                                           data=request.data, partial=True)
                if not serializer.is_valid():
                    pass
                order = serializer.save()

                for order_product in pre_order.order_products.all():
                    order_product.pre_order = None
                    order_product.order = order.id
                    order_product.save()

                # empty pre_order table
                pre_order.products = {}
                pre_order.total = 0
                pre_order.subtotal = 0
                pre_order.save()

                serializer = OrderSerializer(order)

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_update')
    def seller_update_order_product(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')
            campaign_product_id = request.query_params.get(
                'campaign_product_id')
            qty = request.query_params.get(
                'qty') if request.query_params.get('qty') else 0
            _, campaign, pre_order = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)
            campaign_product = Verify.get_campaign_product(
                campaign, campaign_product_id)

            # TODO
            # update
            pre_order
            campaign_product
            qty

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response('test', status=status.HTTP_200_OK)

    # @action(detail=True, methods=['GET'], url_path=r'buyer_update')
    # def buyer_update_order_product(self, request, pk=None):
    #     try:
    #         api_user = request.user.api_users.get(type='customer')
    #         campaign_product_id = request.query_params.get(
    #             'campaign_product_id')
    #         order_product_id = request.query_params.get(
    #             'order_product_id')
    #         qty = request.query_params.get(
    #             'qty') if request.query_params.get('qty') else 0

    #         if not api_user:
    #             raise ApiVerifyError("no user found")
    #         elif api_user.status != "valid":
    #             raise ApiVerifyError("not activated user")
    #         if not api_user.pre_orders.filter(id=pk).exists():
    #             raise ApiVerifyError("not pre_order found")

    #         pre_order = api_user.pre_orders.select_for_update().get(id=pk)

    #         qty_difference = 0

    #         if order_product_id:
    #             if not pre_order.order_products.filter(id=order_product_id).exists():
    #                 pass  # return
    #             order_product = pre_order.order_products.select_for_update().get(
    #                 id=order_product_id)
    #             campaign_product = order_product.campaign_productselect_for_update()
    #             qty_difference = qty-order_product.qty

    #             if qty_difference and campaign_product.qty_for_sale < qty_difference:
    #                 pass
    #                 # return no enough invertory
    #             with transaction.atomic():
    #                 campaign_product.qty_sold = F('qty_sold')-qty_difference
    #                 order_product.qty = qty
    #                 pre_order.products[order_product_id]['qty'] = qty
    #                 pre_order.total = F('total') - \
    #                     (qty_difference*order_product.price)

    #                 campaign_product.save()
    #                 order_product.save()
    #                 pre_order.save()

    #         else:
    #             if pre_order.order_products.filter(campaign_product=campaign_product_id).exist():
    #                 pass  # return
    #             # create
    #             order_product = pre_order.order_products.get(
    #                 campaign_product=campaign_product_id)

    #         campaign_product.qty_for_sale
    #         pre_order
    #         campaign_product
    #         qty

    #     except ApiVerifyError as e:
    #         return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    #     except:
    #         return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #     return Response('test', status=status.HTTP_200_OK)


# from django.db import connection

# with connection.cursor() as cursor:
#     cursor.execute("LOCK TABLES %s READ", [tablename])
#     try:
#         ...
#     finally:
#         cursor.execute("UNLOCK TABLES;")
