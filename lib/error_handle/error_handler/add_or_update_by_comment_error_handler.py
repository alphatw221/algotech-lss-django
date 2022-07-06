
from..error.pre_order_error import PreOrderErrors
import functools, logging, traceback


from pymongo import errors as pymongo_errors

logger = logging.getLogger(__name__)



def add_or_update_by_comment_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PreOrderErrors.PreOrderException as e:
            print(traceback.format_exc())
            return e.state
        except pymongo_errors.PyMongoError as e:
            print(traceback.format_exc())
            return False
        except Exception as e:
            print(traceback.format_exc())
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return False
    return wrapper