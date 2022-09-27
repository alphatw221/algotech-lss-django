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
            print('in ')
            print(key)
            is_valid, developer = lib.helper.token_helper.V1DeveloperTokenHelper.validate_permanent_token(key)
            if is_valid:
                setattr(developer,'is_authenticated',True)
                return (developer,None)
            elif is_valid==None:
                return is_valid
            elif is_valid==False:
                raise exceptions.AuthenticationFailed('Invalid token.')

            # header, payload, signature, api_key, secret_key_hash = key.split('.')

            # header_data = json.loads(base64.urlsafe_b64decode(header+'=='))

            # if header_data.get('typ')!='v1':
            #     return False

            # developer = models.user.developer.Developer.objects.get(api_key=api_key)

            # secret_key_hash_bytes = hmac.new(settings.SECRET_KEY.encode(), msg=developer.secret_key.encode(), digestmod=hashlib.sha256).digest()
            # _secret_key_hash = base64.urlsafe_b64encode(secret_key_hash_bytes).rstrip(b'=').decode('utf-8')
            # if _secret_key_hash!=secret_key_hash:
            #     raise exceptions.AuthenticationFailed('Invalid token.')

            # setattr(developer,'is_authenticated',True)
            # return (developer,None)
        except Exception :
            print(traceback.format_exc())
            raise exceptions.AuthenticationFailed('Invalid token.')


