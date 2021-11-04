from rest_framework import serializers
from dataclasses import dataclass


@dataclass
class FacebookUser:
    user_id: str = ''
    email: str = ''
    name: str = ''
    token: str = ''


class FacebookUserSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    email = serializers.CharField()
    name = serializers.CharField()
    token = serializers.CharField()
