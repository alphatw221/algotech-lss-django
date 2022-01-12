from rest_framework import views, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from django.conf import settings
from api.models.test.sample import Sample, SampleSerializer

from django.core.files.storage import default_storage
from api.utils.common.common import * 
from backend.pymongo.mongodb import db
import traceback
from api.models.order.pre_order import PreOrder


@api_view(['GET'])
def test(request):

    return Response('test accomplished')


@api_view(['GET'])
@api_error_handler
def test_error(request):

    a = PreOrder.objects.get(id=14)
    print (a)

    return Response('test error accomplished')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_api(request, path):
    input = {
        'PATH': path,
        'METHOD': request.method,
        'PARAMS': request.query_params,
        'DATA': request.data,
        'USER_ID': request.user.id,
        'USER_NAME': request.user.username,
    }
    return Response({'input': input})


class TestViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    permission_classes = [IsAdminUser | IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def test(self, request, *args, **kwargs):
        return Response({'msg': 'TestViewSet test accomplished.'})


class SampleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Sample.objects.all().order_by('id')
    serializer_class = SampleSerializer
    filterset_fields = []
