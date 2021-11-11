from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.auto_response.auto_response import AutoResponse, AutoResponseSerializer


class AutoResponseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = AutoResponse.objects.all().order_by('id')
    serializer_class = AutoResponseSerializer
    filterset_fields = []
