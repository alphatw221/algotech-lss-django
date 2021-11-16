from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.user.user import User, UserSerializer

from rest_framework.decorators import action
from django.contrib.auth.models import User as AuthUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filterset_fields = []

    @action(detail=False, methods=['POST'], url_path=r'login')
    def login(self, request, pk=None):

        facebook_id = request.data.get('id')
        facebook_name = request.data.get('name')
        picture = request.data.get('picture')
        email = request.data.get('email')

        auth_user = None
        if not User.objects.filter(email=email).exists():
            auth_user = AuthUser.objects.create_user(
                facebook_name, email, facebook_id)
            user = User.objects.create(email=email)
            user.facebook_info["id"] = facebook_id
            user.facebook_info["name"] = facebook_name
            user.facebook_info["picture"] = picture
            user.save()
        else:
            auth_user = AuthUser.objects.get(email=email)

        refresh = RefreshToken.for_user(auth_user)

        ret = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(ret, status=status.HTTP_200_OK)
