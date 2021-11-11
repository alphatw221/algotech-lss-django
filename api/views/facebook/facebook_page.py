from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.facebook.facebook_page import FacebookPage, FacebookPageSerializer


class FacebookPageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = FacebookPage.objects.all().order_by('id')
    serializer_class = FacebookPageSerializer
    filterset_fields = []
