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
        token = 'EAANwBngXqOABACRnLpEPLpWkFRCGeXy8ZCKR4djZCFof6ZBZCZCGZCulEViYZAt2rZB7SIXYWeE9gXhE5ODeY4vmTtK1ER7cf0ArFAfQGFDAnDN7n0Rq9t6s4Fkm9vRyKZBHBm9Txpk2z3DRuBYPaZByBw73tv3MQu1DN9CiqyTIFCSgCrIkj50GVNH4lgaD6mZBSH9UdN5wZAdZACAZDZD'
        rc, rr = api_fb_get_page_posts(
            token, "109130787659110",)
        pprint.pprint(rc)
        pprint.pprint(rr)
