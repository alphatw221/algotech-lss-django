

from rest_framework import status, viewsets, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings


class FileUploadView(views.APIView):
    parser_classes = [FileUploadParser]

    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        # ...
        # do some stuff with uploaded file
        # ...
        return Response(status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FileUploadParser])
def upload(request, filename):

    api_user = request.user.api_users.get(type='user')
    if not api_user:
        return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
    elif api_user.status != "valid":
        return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)
    print(filename)

    print(request.data)
    file = request.data['file']
    print(type(file))

    path = default_storage.save('tmp/somename.mp3', ContentFile(file).read())
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    # try:

    #
    # except:
    #     return Response('test', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response('test', status=status.HTTP_200_OK)
