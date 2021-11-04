from django.core.management.base import BaseCommand
from api.models.user.user import User, FacebookUser, FacebookUserSerializer


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        t = FacebookUser(user_id='testaaa', token='dsfsdf')
        serializer = FacebookUserSerializer(t)

        user = User.objects.get(id=1)
        user.facebook = serializer.data
        user.save()
        print(user.facebook)
