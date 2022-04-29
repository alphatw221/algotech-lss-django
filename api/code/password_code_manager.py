
from api.code.code_manager import CodeManager
from api.utils.error_handle.error.api_error import ApiVerifyError
from datetime import datetime
from django.contrib.auth.models import User as AuthUser

from service.email.email_service import EmailService
from rest_framework.response import Response
from rest_framework import status
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
            raise ApiVerifyError('code expired') 

        
        if not AuthUser.objects.filter(id=data.get('auth_user_id',-1)).exists():
            raise ApiVerifyError('user not found')

        auth_user = AuthUser.objects.get(id=data.get('auth_user_id'))

        auth_user.set_password(new_password)
        auth_user.save()
        
        # language = data.get('language')
        # EmailService.send_email_template("",auth_user.email,"",{})

        return {
            "User Name":auth_user.username,
            "New Password":new_password[:4]+"*"*(len(new_password)-4)
        }