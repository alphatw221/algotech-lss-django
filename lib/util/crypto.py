from django.conf import settings
import json
from cryptography.fernet import Fernet

__fernet = Fernet(settings.FERNET_KEY.encode())

def encode(data):

    data_str = json.dumps(data)
    return __fernet.encrypt(data_str.encode()).decode()

def decode(code):

    data_str = __fernet.decrypt(code.encode()).decode()
    return json.loads(data_str)
