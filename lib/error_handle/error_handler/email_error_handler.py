import functools, logging, traceback
logger = logging.getLogger(__name__)


def email_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(traceback.format_exc())
            pass
    return wrapper