from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.auto_response.auto_response import AutoResponse, AutoResponseSerializer
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.decorators import action
import io
from rest_framework.parsers import JSONParser
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel


class AutoResponseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = AutoResponse.objects.all().order_by('id')
    serializer_class = AutoResponseSerializer
    filterset_fields = []

    platform_dict = {'facebook': FacebookPage, 'youtube': YoutubeChannel}

    @action(detail=False, methods=['GET'], url_path=r'list_auto_response')
    def list_auto_response(self, request):

        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        if platform_name not in self.platform_dict:
            return Response({"message": "no platfrom name found"}, status=status.HTTP_400_BAD_REQUEST)

        if not self.platform_dict[platform_name].objects.filter(page_id=platform_id).exists():
            return Response({"message": "no platfrom found"}, status=status.HTTP_400_BAD_REQUEST)

        platform = self.platform_dict[platform_name].objects.get(
            page_id=platform_id)
        # TODO 檢查使用者有這個platform的權限

        try:
            auto_responses = platform.auto_responses.all()
            serializer = self.get_serializer(auto_responses, many=True)
        except:
            return Response({"message": "query error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)
