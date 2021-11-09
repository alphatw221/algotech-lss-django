from django.core.management.base import BaseCommand
from api.models.user.user import User
from api.models.user.facebook_info import FacebookInfo, FacebookInfoSerializer
from api.utils.api.facebook.user import api_fb_me


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        api_fb_me('EAANwBngXqOABAIdePIFce0LlMlN5QogbsihP2paRAiGtunqsVmcrxwhFjcDYZArL0jvhaalblb3fhYOTgMgjweLMyBrMVvezA8L1CR0Q2cSy1nOg43t1xEksQmhQ3xLR7d6znCRvv7n79tl5poEuGO39u67pZBP1nc2gRL6ta1FiNLZAam081n2hVykp5JqQrU7STA6CCorcnZBnM5ukJ9pDdEWBSHUZD')
