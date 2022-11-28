from lib import error_handle
from .code_manager import CodeManager
from datetime import datetime
from django.contrib.auth.models import User as AuthUser

class PasswordResetCodeManager(CodeManager):

    code_key="reset_password"

    data_format = [
        "auth_user_id",
        "language",
        "expired_time",
    ]

    @classmethod
    def generate(cls,auth_user_id,language):

        data={
            'auth_user_id':auth_user_id,
            'language':language,
            'expired_time':datetime.now().timestamp()+3000
        }

        return cls._encode(data)

    
    
    @classmethod
    def execute(cls, code, new_password):

        data = cls._decode(code)

        if float(data.get('expired_time', 1)) <datetime.now().timestamp():
            raise  error_handle.error.api_error.ApiVerifyError('reset_password_code_manager.code_expired') 

        
        if not AuthUser.objects.filter(id=data.get('auth_user_id',-1)).exists():
            raise  error_handle.error.api_error.ApiVerifyError('user_not_found')

        auth_user = AuthUser.objects.get(id=data.get('auth_user_id'))

        auth_user.set_password(new_password)
        auth_user.save()
        
        # language = data.get('language')
        # EmailService.send_email_template("",auth_user.email,"",{})

        return {
            "user_name":auth_user.username,
            "email":auth_user.email,
            "new_password":new_password[:4]+"*"*(len(new_password)-4)
        }