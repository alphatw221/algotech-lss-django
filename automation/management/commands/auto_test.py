import threading
import pendulum
import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        threading.Thread(target=time_loop, args=(test_mod, 5),
                         daemon=True).start()

        waiting_for_SIGINT = threading.Event().wait()


def time_loop(func, sleep_time):
    while True:
        try:
            func()
        except:
            ...
        finally:
            ...
        time.sleep(sleep_time)


def test_mod():
    print(pendulum.now())
