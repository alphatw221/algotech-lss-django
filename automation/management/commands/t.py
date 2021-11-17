from django.core.management.base import BaseCommand
from api.models.campaign.campaign import Campaign
from api.utils.api.facebook.page import *
from api.utils.api.facebook.user import *
from api.utils.api.facebook.post import *
from api.utils.common.facebook.post_comment import *
from api.utils.orm.campaign import *
import pprint


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print(get_active_campaign_now())
