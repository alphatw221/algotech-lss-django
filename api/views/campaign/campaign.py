from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign import Campaign, CampaignSerializer
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.decorators import action
import io
from rest_framework.parsers import JSONParser


class CampaignViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Campaign.objects.all().order_by('id')
    serializer_class = CampaignSerializer
    filterset_fields = []

    @action(detail=False, methods=['POST'], url_path=r'create_campaign')
    def create_campaign(self, request):

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            json = io.BytesIO(request.body)
            data = JSONParser().parse(json)
            data['created_by'] = api_user.id
            serializer = self.get_serializer(data=data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

        except:
            return Response({"message": "error occerd during creating"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_campaign')
    def list_campaign(self, request):

        order_by = request.query_params.get('order_by')
        product_status = request.query_params.get('status')
        key_word = request.query_params.get('key_word')

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.queryset.filter(user=api_user)

        try:
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

    @action(detail=False, methods=['GET'], url_path=r'update_campaign')
    def update_campaign(self, request):

        request.data.get('title')
        request.data.get('description')
        request.data.get('start_at')
        request.data.get('end_at')
        request.data.get('type')
        request.data.get('status')
        request.data.get('facebook_page')
        request.data.get('facebook_campaign')
        request.data.get('youtube_channel')
        request.data.get('youtube_campaign')
        request.data.get('meta')
        request.data.get('payment_info')
        request.data.get('logistics_info')

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.queryset.filter(user=api_user)

        try:
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
