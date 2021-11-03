from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from ..models.sample import Sample, SampleSerializer


class SampleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Sample.objects.all().order_by('id')
    serializer_class = SampleSerializer
    filterset_fields = []
