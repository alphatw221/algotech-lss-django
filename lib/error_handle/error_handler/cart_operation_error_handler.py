
from rest_framework.response import Response
from rest_framework import status
import lib

import functools, logging, traceback
logger = logging.getLogger(__name__)

import lib

def update_cart_product_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
       
        except lib.error_handle.error.cart_error.CartErrors.CartException as e:
            print(traceback.format_exc())
            return Response({"message": str(e), "params":e.params}, status=status.HTTP_400_BAD_REQUEST)
        
    return wrapper


def update_cart_product_by_comment_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except lib.error_handle.error.cart_error.CartErrors.CartException as e:
            print(traceback.format_exc())
            return e.state
    return wrapper