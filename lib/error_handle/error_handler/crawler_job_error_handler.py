from api.utils.error_handle.error.pre_order_error import PreOrderErrors
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime
from backend.google_cloud_logging.google_cloud_logging import ApiLogEntry
import functools, logging, traceback


from pymongo import errors as pymongo_errors

logger = logging.getLogger(__name__)



def crawler_job_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pymongo_errors.PyMongoError as e:
            print(traceback.format_exc())
            return False
        except Exception as e:
            print(traceback.format_exc())
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return False
    return wrapper