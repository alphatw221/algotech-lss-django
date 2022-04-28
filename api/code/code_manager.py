from django.conf import settings

from api.utils.error_handle.error.api_error import ApiVerifyError

from cryptography.fernet import Fernet
class CodeManager():

    code_key=""

    data_format = {}

    _fernet = Fernet(settings.FERNET_KEY.encode())

    @classmethod
    def _encode(cls, data):

        data["code_key"]=cls.code_key
        data["secret_key"]=settings.FERNET_KEY

        message_string = ""
        for _, value in data.items():
            message_string+=str(value)+"|"
        return cls._fernet.encrypt(message_string[:-1].encode()).decode()

    @classmethod
    def _decode(cls, code):
        try:
            message_string = cls._fernet.decrypt(code.encode()).decode()
        except Exception:
            raise ApiVerifyError('invalid token')
            
        parameters = message_string.split('|')

        data = cls.data_format.copy()
        if len(parameters) != len(data)+2:
            raise ApiVerifyError('subscription code not valid')
        
        if parameters[-2] != cls.code_key or parameters[-1] != settings.FERNET_KEY:
            raise ApiVerifyError('code not valid')

        for i ,(key, _) in enumerate(data.items()):
            data[key] = parameters[i]

        return data

    @classmethod
    def generate(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def execute(cls, *args, **kwargs):
        raise NotImplementedError









