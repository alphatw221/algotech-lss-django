from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from api import models
import lib

class AutoResponsePagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'

class AutoResponseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.auto_response.auto_response.AutoResponse.objects.all().order_by('id')
    serializer_class = models.auto_response.auto_response.AutoResponseSerializer


    # platform_dict = {'facebook': FacebookPage,
    #                  'youtube': YoutubeChannel}

    pagination_class = AutoResponsePagination
    
    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_auto_response(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        auto_response = lib.util.verify.Verify.get_auto_response_from_user_subscription(user_subscription, pk)

        return Response(models.auto_response.auto_response.AutoResponseSerializer(auto_response).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_auto_response(self, request):
        api_user, keyword,  = lib.util.getter.getparams(request, ("keyword", ), with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        print (keyword)

        if keyword in [None, '']:
            auto_responses = user_subscription.auto_responses.all().order_by("-created_at")
        else:
            auto_responses = user_subscription.auto_responses.filter(input_msg__icontains=keyword).order_by("-created_at")
        
        page = self.paginate_queryset(auto_responses)
        serializer = models.auto_response.auto_response.AutoResponseSerializerWithPagesInfo(page, many=True)

        return Response(self.get_paginated_response(serializer.data).data, status=status.HTTP_200_OK)


    # @action(detail=False, methods=['POST'], url_path=r'create/(?P<platform_name>[^/.]+)/(?P<platform_id>[^/.]+)', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def create_auto_response(self, request, platform_name, platform_id):

    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     platform = lib.util.verify.Verify.get_platform_from_user_subscription(user_subscription, platform_name, platform_id)

    #     data = request.data
    #     data['input_msg'] = data['input_msg'].lower()
    #     data['user_subscription'] = user_subscription.id

    #     if platform_name == 'facebook':
    #         data['facebook_page'] = platform.id
    #     elif platform_name == 'youtube':
    #         data['youtube_channel'] = platform.id
    #     elif platform_name == 'instagram':
    #         data['instagram_profile'] = platform.id

    #     serializer = models.auto_response.auto_response.AutoResponseSerializer(data=data)
    #     if not serializer.is_valid():
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     obj = serializer.save()
        
    #     return Response(models.auto_response.auto_response.AutoResponseSerializerWithPagesInfo(obj).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_auto_response(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        data = request.data
        data['input_msg'] = data['input_msg'].lower()
        data['user_subscription'] = user_subscription.id
        for chosen_page in data.get('chosenPage'):
            platform_name = 'facebook' if chosen_page.get('page_id') else 'instagram'
            platform_id = chosen_page.get('id')
            platform = lib.util.verify.Verify.get_platform_from_user_subscription(user_subscription, platform_name, platform_id)
            if platform_name == 'facebook':
                data['facebook_page'] = platform.id
            elif platform_name == 'youtube':
                data['youtube_channel'] = platform.id
            elif platform_name == 'instagram':
                data['instagram_profile'] = platform.id
            
            serializer = models.auto_response.auto_response.AutoResponseSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            obj = serializer.save()

        return Response({'message': 'create success'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['PUT'], url_path=r'update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_auto_response(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        auto_response = lib.util.verify.Verify.get_auto_response_from_user_subscription(user_subscription, pk)

        data = request.data
        data['input_msg'] = data['input_msg'].lower()
        
        serializer = models.auto_response.auto_response.AutoResponseSerializerUpdate(
            auto_response, data=data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_auto_response(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        auto_response = lib.util.verify.Verify.get_auto_response_from_user_subscription(user_subscription, pk)

        auto_response.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'batch/delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_auto_response(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if type(request.data) == list:
            for reply_id in request.data:
                auto_response = lib.util.verify.Verify.get_auto_response_from_user_subscription(user_subscription, reply_id)
                auto_response.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

