import pendulum
import time
from django.core.management.base import BaseCommand
from api.models.sample import Sample


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            for _ in range(10):
                print(f'{pendulum.now()} - {Sample.objects.all().count()=}')
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Stopped'))
