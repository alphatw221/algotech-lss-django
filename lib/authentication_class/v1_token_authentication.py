from rest_framework import authentication
from rest_framework import exceptions

from django.conf import settings

from api import models

import hashlib, hmac
import json, base64
import traceback
import lib


class V1PermanentTokenAuthentication(authentication.TokenAuthentication):

    keyword = 'Token'
    model = None
    
    def authenticate_credentials(self, key):
        try:
            is_valid, developer = lib.helper.token_helper.V1DeveloperTokenHelper.validate_permanent_token(key)

            if is_valid:
                setattr(developer,'is_authenticated',True)
                return (developer,None)
            elif is_valid==None:
                return None
            elif is_valid==False:
                raise exceptions.AuthenticationFailed('Invalid token.')

        except Exception :
            print(traceback.format_exc())
            raise exceptions.AuthenticationFailed('Invalid token.')


