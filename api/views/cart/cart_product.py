from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign import Campaign
from api.models.cart.cart_product import CartProduct, CartProductSerializer, CartProductSerializerCreate, CartProductSerializerUpdate
from rest_framework.response import Response
from rest_framework.decorators import action

from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError


def verify_seller_request(api_user, platform_name, platform_id, campaign_id, cart_product_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)

    if cart_product_id:
        if not campaign.cart_products.filter(id=cart_product_id).exists():
            raise ApiVerifyError('no campaign product found')
        cart_product = campaign.cart_puroducts.get(id=cart_product_id)
        return platform, campaign, cart_product

    return platform, campaign


def verify_buyer_request(api_user, campaign_id, campaign_product_id=None):
    if not api_user:
        raise ApiVerifyError("no user found")

    if not Campaign.objects.filter(id=campaign_id).exists():
        raise ApiVerifyError("no campaign found")
    campaign = Campaign.objects.get(id=campaign_id)

    if campaign_product_id:
        if not campaign.cart_products.filter(id=campaign_product_id).exists():
            raise ApiVerifyError('no campaign product found')
        campaign_product = campaign.cart_puroducts.get(id=campaign_product_id)
        return campaign, campaign_product

    return campaign


class CartProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CartProduct.objects.all().order_by('id')
    serializer_class = CartProductSerializer
    filterset_fields = []

    @action(detail=True, methods=['GET'], url_path=r'seller_retrieve_cart_product')
    def seller_retrieve_cart_product(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, cart_product = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id, cart_product_id=pk)

            serializer = self.get_serializer(cart_product)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller_list_cart_product')
    def seller_list_cart_product(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')
            _, campaign = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id)
            # TODO fillter
            campaign_products = campaign.cart_products.all()
            serializer = self.get_serializer(campaign_products, many=True)

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "query error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'seller_create_cart_product')
    def seller_create_cart_product(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            campaign_product_id = request.query_params.get(
                'campaign_product_id')
            api_user = request.user.api_users.get(type='user')

            _, campaign = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id)

            if not campaign.products.filter(id=campaign_product_id).exists():
                raise ApiVerifyError('no campaign_product found')

            # TODO 檢查庫存 狀態

            data = request.data
            data['campaign'] = campaign_id
            data['campaign_product'] = campaign_product_id
            serializer = CartProductSerializerCreate(data=data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during creating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'seller_update_cart_product')
    def seller_update_cart_product(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, cart_product = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id, cart_product_id=pk)

            # TODO 檢查庫存 狀態
            serializer = CartProductSerializerUpdate(
                cart_product, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during updating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'seller_delete_cart_product')
    def seller_delete_cart_product(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, cart_product = verify_seller_request(
                api_user, platform_name, platform_id, campaign_id, cart_product_id=pk)

            cart_product.delete()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during deleting"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_list_cart_product')
    def buyer_list_cart_product(self, request):
        pass

    @action(detail=False, methods=['POST'], url_path=r'buyer_create_cart_product')
    def buyer_create_cart_product(self, request):
        try:
            campaign_id = request.query_params.get('campaign_id')
            campaign_product_id = request.query_params.get(
                'campaign_product_id')
            api_user = request.user.api_users.get(type='customer')

            campaign, campaign_product = verify_buyer_request(
                api_user, campaign_id, campaign_product_id)

            # TODO 檢查庫存 狀態
            data = request.data
            data['campaign'] = campaign_id
            data['campaign_product'] = campaign_product_id
            date['']
            serializer = CartProductSerializerCreate(data=data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during creating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'buyer_update_cart_product')
    def buyer_update_cart_product(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, cart_product = verify_request(
                api_user, platform_name, platform_id, campaign_id, cart_product_id=pk)

            # TODO 檢查庫存 狀態
            serializer = CartProductSerializerUpdate(
                cart_product, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during updating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'buyer_delete_cart_product')
    def buyer_delete_cart_product(self, request, pk=None):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            api_user = request.user.api_users.get(type='user')

            _, _, cart_product = verify_request(
                api_user, platform_name, platform_id, campaign_id, cart_product_id=pk)

            cart_product.delete()

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "error occerd during deleting"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)
