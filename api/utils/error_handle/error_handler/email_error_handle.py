from rest_framework.response import Response
from rest_framework import status

from datetime import datetime
from backend.google_cloud_logging.google_cloud_logging import ApiLogEntry
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
            #TODO record error log
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return Response({"message": str(datetime.now())+"server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper