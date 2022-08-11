
from api.utils.error_handle.error.cart_error import CartErrors
from rest_framework.response import Response
from rest_framework import status

import functools, logging, traceback
logger = logging.getLogger(__name__)

import lib

def order_operation_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
       
        except CartErrors.CartException as e:
            print(traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    return wrapper