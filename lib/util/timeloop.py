import time
import traceback


def time_loop(sleep_time):
    def decorator(func):
        def wrapper(*args, **kwargs):
            while True:
                output = func(*args, **kwargs)
                if output=='break':
                    break
                time.sleep(sleep_time)
        return wrapper
    return decorator

def infinite_loop():
    def decorator(func):
        def wrapper(*args, **kwargs):
            while True:
                func(*args, **kwargs)
        return wrapper
    return decorator


def interval(times=1, interval=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times) :
                output = func(*args, **kwargs)
                if output=='break':
                    break
                time.sleep(interval)
        return wrapper
    return decorator