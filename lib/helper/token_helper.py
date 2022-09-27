
from email import header
import hashlib, hmac
import json, base64
import traceback
from django.conf import settings
from datetime import datetime, timedelta
from api import models

class V1DeveloperTokenHelper:

    header_data = header_data = {
                'alg':'sha256',
                'typ':'v1'
            }

    @classmethod
    def generate_token(cls, developer=None, developer_id=None):
            

        header_json = json.dumps(cls.header_data)
        header = base64.urlsafe_b64encode(header_json.encode('utf-8')).rstrip(b'=').decode('utf-8')

        if not developer:
            developer = models.user.developer.Developer.objects.get(id = developer_id)

        payload_1_data = {
            'key':developer.api_key, 
            'perm':developer.permissions,
            'auth':developer.authorization,
            'meta':developer.meta,
            'exp':int((datetime.now()+timedelta(days=7)).timestamp())
        }
        payload_1_json = json.dumps(payload_1_data)
        payload_1 = base64.urlsafe_b64encode(payload_1_json.encode('utf-8')).rstrip(b'=').decode('utf-8')

        head_and_claim = header+'.'+payload_1
        signature_1 = hmac.new(settings.SECRET_KEY.encode(), msg=head_and_claim.encode(), digestmod=hashlib.sha256).hexdigest()

        secret_key_hash_bytes = hmac.new(settings.SECRET_KEY.encode(), msg=developer.secret_key.encode(), digestmod=hashlib.sha256).digest()

        secret_key_hash = base64.urlsafe_b64encode(secret_key_hash_bytes).rstrip(b'=').decode('utf-8')
        token = head_and_claim+'.'+signature_1+'.'+developer.api_key+'.'+secret_key_hash
        
        return token


    @classmethod
    def validate_permanent_token(cls, token):
        
        try:
            print('in helper')
            header, payload, signature, api_key, secret_key_hash = token.split('.')   #permanent_token no need payload and signature

            header_data = json.loads(base64.urlsafe_b64decode(header+'=='))
            print(header_data)
            if header_data!=cls.header_data:

                return None, None

            developer = models.user.developer.Developer.objects.get(api_key=api_key)
            print(developer)
            secret_key_hash_bytes = hmac.new(settings.SECRET_KEY.encode(), msg=developer.secret_key.encode(), digestmod=hashlib.sha256).digest()
            _secret_key_hash = base64.urlsafe_b64encode(secret_key_hash_bytes).rstrip(b'=').decode('utf-8')
            
            if _secret_key_hash == secret_key_hash:
                True, developer
        except Exception:
            print(traceback.format_exc())
            return False, None
        return False, None