import time
import traceback


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
