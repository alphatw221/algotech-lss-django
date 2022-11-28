from lib.error_handle.error.api_error import ApiCallerError, ApiVerifyError

from datetime import datetime
import functools, logging, traceback
logger = logging.getLogger(__name__)



def web_socket_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiCallerError as e:
            print(traceback.format_exc())

        except ApiVerifyError as e:
            print(traceback.format_exc())
            
        except Exception as e:
            print(traceback.format_exc())
            
    return wrapper