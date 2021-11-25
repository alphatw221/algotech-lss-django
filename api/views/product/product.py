from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api.models.product.product import Product, ProductSerializer
from rest_framework.decorators import action
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from backend.api.facebook.user import api_fb_get_me_accounts


class ProductPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'

    # django_paginator_class - The Django Paginator class to use. Default is django.core.paginator.Paginator, which should be fine for most use cases.
    # page_size - A numeric value indicating the page size. If set, this overrides the PAGE_SIZE setting. Defaults to the same value as the PAGE_SIZE settings key.
    # page_query_param - A string value indicating the name of the query parameter to use for the pagination control.
    # page_size_query_param - If set, this is a string value indicating the name of a query parameter that allows the client to set the page size on a per-request basis. Defaults to None, indicating that the client may not control the requested page size.
    # max_page_size - If set, this is a numeric value indicating the maximum allowable requested page size. This attribute is only valid if page_size_query_param is also set.
    # last_page_strings - A list or tuple of string values indicating values that may be used with the page_query_param to request the final page in the set. Defaults to ('last',)
    # template - The name of a template to use when rendering pagination controls in the browsable API. May be overridden to modify the rendering style, or set to None to disable HTML pagination controls completely. Defaults to "rest_framework/pagination/numbers.html".


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = []
    pagination_class = ProductPagination

    platform_dict = {'facebook': FacebookPage,
                     'youtube': YoutubeChannel}

    @action(detail=True, methods=['GET'], url_path=r'retrieve_product')
    def retrieve_product(self, request, pk=None):

        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')

        api_user = request.user.api_users.get(type='user')
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if platform_name not in self.platform_dict:
            return Response({"message": "no platfrom name found"}, status=status.HTTP_400_BAD_REQUEST)

        if not self.platform_dict[platform_name].objects.filter(id=platform_id).exists():
            return Response({"message": "no platfrom found"}, status=status.HTTP_400_BAD_REQUEST)
        platform = self.platform_dict[platform_name].objects.get(
            id=platform_id)

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        user_subscriptions = platform.user_subscriptions.all()
        if not user_subscriptions:
            return Response({"message": "platform not in any user_subscription"}, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = user_subscriptions[0]

        if not user_subscription.products.filter(id=pk).exists():
            return Response({"message": "no product found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = user_subscription.products.get(id=pk)
            serializer = self.get_serializer(product)
        except:
            return Response({"message": "error occerd during retriving"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_product')
    def list_product(self, request):

        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')

        order_by = request.query_params.get('order_by')
        product_status = request.query_params.get('status')
        key_word = request.query_params.get('key_word')

        api_user = request.user.api_users.get(type='user')
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if platform_name not in self.platform_dict:
            return Response({"message": "no platfrom name found"}, status=status.HTTP_400_BAD_REQUEST)

        if not self.platform_dict[platform_name].objects.filter(id=platform_id).exists():
            return Response({"message": "no platfrom found"}, status=status.HTTP_400_BAD_REQUEST)
        platform = self.platform_dict[platform_name].objects.get(
            id=platform_id)

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        user_subscriptions = platform.user_subscriptions.all()
        if not user_subscriptions:
            return Response({"message": "platform not in any user_subscription"}, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = user_subscriptions[0]

        try:
            queryset = user_subscription.products.all()
            if product_status:
                queryset = queryset.filter(status=product_status)
            if key_word:
                queryset = queryset.filter(name__icontains=key_word)
            if order_by:
                queryset = queryset.order_by(order_by)
        except:
            return Response({"message": "query error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_product')
    def create_product(self, request):

        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')

        api_user = request.user.api_users.get(type='user')
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if platform_name not in self.platform_dict:
            return Response({"message": "no platfrom name found"}, status=status.HTTP_400_BAD_REQUEST)

        if not self.platform_dict[platform_name].objects.filter(id=platform_id).exists():
            return Response({"message": "no platfrom found"}, status=status.HTTP_400_BAD_REQUEST)
        platform = self.platform_dict[platform_name].objects.get(
            id=platform_id)

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        user_subscriptions = platform.user_subscriptions.all()
        if not user_subscriptions:
            return Response({"message": "platform not in any user_subscription"}, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = user_subscriptions[0]

        try:

            data = request.data
            data['user_subscription'] = user_subscription.id
            serializer = self.get_serializer(data=data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except:
            return Response({"message": "error occerd during creating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update_product')
    def update_product(self, request, pk=None):

        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')

        api_user = request.user.api_users.get(type='user')
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if platform_name not in self.platform_dict:
            return Response({"message": "no platfrom name found"}, status=status.HTTP_400_BAD_REQUEST)

        if not self.platform_dict[platform_name].objects.filter(id=platform_id).exists():
            return Response({"message": "no platfrom found"}, status=status.HTTP_400_BAD_REQUEST)
        platform = self.platform_dict[platform_name].objects.get(
            id=platform_id)

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        user_subscriptions = platform.user_subscriptions.all()
        if not user_subscriptions:
            return Response({"message": "platform not in any user_subscription"}, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = user_subscriptions[0]

        if not user_subscription.products.filter(id=pk).exists():
            return Response({"message": "no product found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = user_subscription.products.get(id=pk)
            serializer = self.get_serializer(
                product, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except:
            return Response({"message": "error occerd during updating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete_product')
    def delete_product(self, request, pk=None):

        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')

        api_user = request.user.api_users.get(type='user')
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if platform_name not in self.platform_dict:
            return Response({"message": "no platfrom name found"}, status=status.HTTP_400_BAD_REQUEST)

        if not self.platform_dict[platform_name].objects.filter(id=platform_id).exists():
            return Response({"message": "no platfrom found"}, status=status.HTTP_400_BAD_REQUEST)
        platform = self.platform_dict[platform_name].objects.get(
            id=platform_id)

        if not is_admin(platform_name, api_user, platform):
            return Response({"message": "user is not platform admin"}, status=status.HTTP_400_BAD_REQUEST)

        user_subscriptions = platform.user_subscriptions.all()
        if not user_subscriptions:
            return Response({"message": "platform not in any user_subscription"}, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = user_subscriptions[0]

        if not user_subscription.products.filter(id=pk).exists():
            return Response({"message": "no product found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_subscription.products.get(id=pk).delete()
        except:
            return Response({"message": "error occerd during deleting"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)


def is_admin(platform_name, api_user, platform):
    try:
        if platform_name == 'facebook':
            status_code, response = api_fb_get_me_accounts(
                api_user.facebook_info['token'])

            for item in response['data']:
                if item['id'] == platform.page_id:
                    return True
            return False
        elif platform_name == 'youtube':
            pass
    except:
        return False
    return False
