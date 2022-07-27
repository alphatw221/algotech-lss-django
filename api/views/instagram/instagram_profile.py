
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.instagram.instagram_profile import InstagramProfile, InstagramProfileSerializer


class InstagramViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = InstagramProfile.objects.all().order_by('id')
    serializer_class = InstagramProfileSerializer
    filterset_fields = []