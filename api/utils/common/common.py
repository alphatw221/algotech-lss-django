from api.utils.common.verify import ApiVerifyError
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime
from backend.google_cloud_logging.google_cloud_logging import ApiLogEntry
import functools, logging, traceback
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


def getparams(request, params: tuple, with_user=True, seller=True):
    ret=[]
    if with_user:
        if seller:
            if not request.user.api_users.filter(type='user').exists():
                raise ApiVerifyError('no api_user found')
            ret = [request.user.api_users.get(type='user')]
        else:
            if not request.user.api_users.filter(type='customer').exists():
                raise ApiVerifyError('no api_user found')
            ret = [request.user.api_users.get(type='customer')]
    for param in params:
        ret.append(request.query_params.get(param, None))
    return ret

def getdata(request, data: tuple):
    ret = []
    for d in data:
        ret.append(request.data.get(d, None))
    return ret


def api_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiVerifyError as e:
            # ApiLogEntry.write_entry(str(datetime.now()) + ' - ' +  traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
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