from django.core.management.base import BaseCommand
from api.models.user.user import User
from api.models.user.facebook_info import FacebookInfo, FacebookInfoSerializer


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        t = FacebookInfo(user_id='testaaa', token='dsfsdf')
        serializer = FacebookInfoSerializer(t)

        user = User.objects.get(id=1)
        user.facebook = serializer.data
        user.save()
        print(user.facebook)
