from django.core.management.base import BaseCommand
from api.utils.api.facebook.page import *
from api.utils.api.facebook.user import *
from api.utils.api.facebook.post import *
import pprint


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        token = 'EAANwBngXqOABACkzcVQLUj2pypO5r9aVXySsg4FJZAynAZBYoJfCVteHNgfUh9QbGEnOZBxXgdDJFofwLi49vIp5ZC1h3NXw71oAUv0mpgFzDa19aoRID4QVnc4C5Tbc0r8JXBunHLTMoPELVURVOQoOYZAxTsw3IThx9fyajyurrBIfZAHsyRtlKs5Kw01NcTULERgrgyWSpvKm2RGQnZAzlihRpmPL90ZD'
        rc, rr = api_fb_get_post_likes(
            token, '109130787659110_1014690035757404')
        pprint.pprint(rc)
        pprint.pprint(rr)
