from django.core.management.base import BaseCommand
from api.models.sample import Sample


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        ...
