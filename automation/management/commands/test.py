import pendulum
import time
from django.core.management.base import BaseCommand
from api.models.sample import Sample


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for i in range(5):
            Sample.objects.create(title=f'{pendulum.now()}', integer=i)

            time.sleep(5)

        self.stdout.write(self.style.SUCCESS('done'))
