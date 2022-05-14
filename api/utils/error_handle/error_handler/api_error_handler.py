from api.utils.error_handle.error.api_error import ApiCallerError, ApiVerifyError
from api.utils.error_handle.error.pre_order_error import PreOrderErrors
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime
from api.utils.error_handle.error_handler.pymongo_error_handler import pymongo_error_handler
from backend.google_cloud_logging.google_cloud_logging import ApiLogEntry
import functools, logging, traceback
from django.core.exceptions import ObjectDoesNotExist
from pymongo import errors as pymongo_errors
logger = logging.getLogger(__name__)



def api_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiCallerError as e:
            print(traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ApiVerifyError as e:
            print(traceback.format_exc())
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            print('error is raised')
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            print(traceback.format_exc())
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            print(traceback.format_exc())
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except PreOrderErrors.PreOrderException as e:
            print(traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except pymongo_errors.PyMongoError as e:
            print(traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return Response({"message": str(datetime.now())+"server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper