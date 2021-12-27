from api.utils.common.verify import ApiVerifyError
from rest_framework.response import Response
from rest_framework import status

import functools
from datetime import datetime


def getparams(request, params: tuple, seller=True):
    if seller:
        if not request.user.api_users.filter(type='user').exists():
            raise ApiVerifyError('no api_user found')
        ret = [request.user.api_users.get(type='user')]
    else:
        if not request.user.api_users.filter(type='customer').exists():
            raise ApiVerifyError('no api_user found')
        ret = [request.user.api_users.get(type='customer')]
    for param in params:
        ret.append(request.query_params.get(param))
    return ret


def api_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"message": str(datetime.now())+"server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper