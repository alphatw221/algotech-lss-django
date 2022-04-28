from django.conf import settings

from api.utils.error_handle.error.api_error import ApiVerifyError

from cryptography.fernet import Fernet
class CodeManager():

    code_key=""

    data_format = []

    _fernet = Fernet(settings.FERNET_KEY.encode())

    @classmethod
    def _encode(cls, data):

        # data["code_key"]=cls.code_key
        # data["secret_key"]=settings.FERNET_KEY

        message_string = ""
        for key in cls.data_format:
            message_string+=str(data[key])+"|"

        message_string+=cls.code_key+"|"
        message_string+=settings.FERNET_KEY

        return cls._fernet.encrypt(message_string.encode()).decode()

    @classmethod
    def _decode(cls, code):
        try:
            message_string = cls._fernet.decrypt(code.encode()).decode()
        except Exception:
            raise ApiVerifyError('invalid token')
            
        parameters = message_string.split('|')

        # data = cls.data_format.copy()
        if len(parameters) != len(cls.data_format)+2:
            raise ApiVerifyError('subscription code not valid')
        
        if parameters[-2] != cls.code_key or parameters[-1] != settings.FERNET_KEY:
            raise ApiVerifyError('code not valid')

        data = {}
        for i ,key in enumerate(cls.data_format):
            data[key] = parameters[i]

        return data

    @classmethod
    def generate(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def execute(cls, *args, **kwargs):
        raise NotImplementedError









