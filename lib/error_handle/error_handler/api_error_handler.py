from api.utils.error_handle.error.pre_order_error import PreOrderErrors
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime
# from backend.google_cloud_logging.google_cloud_logging import ApiLogEntry
import functools, logging, traceback
from django.core.exceptions import ObjectDoesNotExist
logger = logging.getLogger(__name__)

import lib

def api_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except lib.error_handle.error.api_error.ApiCallerError as e:
        # except ApiCallerError as e:
            print(traceback.format_exc())
            params = e.params
            return Response({"message": str(e), "params":params}, status=status.HTTP_400_BAD_REQUEST)
        # except ApiVerifyError as e:
        except lib.error_handle.error.api_error.ApiVerifyError as e:
            print(traceback.format_exc())
            params = e.params
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            print('error is raised')
            print({"message": str(e), **params})
            return Response({"message": str(e), "params":params}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            print(traceback.format_exc())
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            print(traceback.format_exc())
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(traceback.format_exc())
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return Response({"message": str(datetime.now())+"server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper