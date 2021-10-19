from rest_framework import viewsets
from ..models.sample import Sample, SampleSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated


class SampleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, IsAuthenticated)
    queryset = Sample.objects.all().order_by('id')
    serializer_class = SampleSerializer
    filterset_fields = ['integer']
