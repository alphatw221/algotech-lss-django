import functools, logging
from pymongo import errors as pymongo_errors


def pymongo_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pymongo_errors.PyMongoError as e:
            print(e)
            raise pymongo_errors.PyMongoError("server busy, please try again")
    return wrapper