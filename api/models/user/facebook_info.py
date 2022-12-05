from rest_framework import serializers
from dataclasses import dataclass


@dataclass
class FacebookInfo:
    user_id: str = ''
    email: str = ''
    name: str = ''
    token: str = ''


class FacebookInfoSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    token = serializers.CharField(required=False)
    picture = serializers.CharField(required=False)
