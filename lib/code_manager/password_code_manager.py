from .code_manager import CodeManager
from datetime import datetime
from django.contrib.auth.models import User as AuthUser


import lib

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
            raise  lib.error_handle.error.api_error.ApiVerifyError('code expired') 

        
        if not AuthUser.objects.filter(id=data.get('auth_user_id',-1)).exists():
            raise  lib.error_handle.error.api_error.ApiVerifyError('user not found')

        auth_user = AuthUser.objects.get(id=data.get('auth_user_id'))

        auth_user.set_password(new_password)
        auth_user.save()
        
        # language = data.get('language')
        # EmailService.send_email_template("",auth_user.email,"",{})

        return {
            "Customer Name":auth_user.username,
            "Email":auth_user.email,
            "New Password":new_password[:4]+"*"*(len(new_password)-4)
        }