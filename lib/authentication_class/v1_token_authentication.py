from rest_framework import authentication
from rest_framework import exceptions
import traceback
from lib import helper


class V1PermanentTokenAuthentication(authentication.TokenAuthentication):

    keyword = 'Token'
    model = None
    
    def authenticate_credentials(self, key):
        try:
            is_valid, developer = helper.token_helper.V1DeveloperTokenHelper.validate_permanent_token(key)

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


