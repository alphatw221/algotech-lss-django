import threading
import time
import traceback
import pendulum
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        threading.Thread(target=print_now, daemon=True).start()

        waiting_for_SIGINT = threading.Event().wait()


def time_loop(sleep_time):
    def decorator(func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except Exception:
                    print(traceback.format_exc())
                time.sleep(sleep_time)
        return wrapper
    return decorator


@time_loop(5)
def print_now():
    print(pendulum.now())
