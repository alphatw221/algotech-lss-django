from django.conf import settings
from django.contrib.auth.models import User as AuthUser

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from api.utils.common.verify import Verify
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.verify import ApiVerifyError
from api import models

import service
import business_policy
import lib

from datetime import datetime, timedelta
import string, random
class HubspotViewSet(viewsets.GenericViewSet):
    queryset = models.user.user.User.objects.none()

    @action(detail=False, methods=['POST'], url_path=r'registration/webhook', permission_classes=())
    @api_error_handler
    def handle_new_registeration_from_hubspot(self, request):

        Verify.is_hubspot_signature_valid(request,'POST', f'{settings.GCP_API_LOADBALANCER_URL}/api/hubspot/registration/webhook/')

        first_name, last_name, email, country, subscription_type, country_code, phone = \
            lib.util.getter.getproperties(request.data.get('properties'),('firstname','lastname','email','country','subscription_type','country_code','phone'), nest_property='value')

        password = ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8))
        country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country)

        if AuthUser.objects.filter(email = email).exists() or models.user.user.User.objects.filter(email=email, type='user').exists():
            raise ApiVerifyError('This email address has already been registered.')

        now = datetime.now() 
        expired_at = now+timedelta(days=30)

        auth_user = AuthUser.objects.create_user(
            username=f'{first_name} {last_name}', email=email, password=password)
        
        user_subscription = models.user.user_subscription.UserSubscription.objects.create(
            name=f'{first_name} {last_name}', 
            status='new', 
            expired_at=expired_at, 
            user_plan= {"activated_platform" : ["facebook"]}, 
            meta_country={ 'activated_country': [country] },
            type='trial',
            lang=country_plan.language  
            )
        
        models.user.user.User.objects.create(name=f'{first_name} {last_name}', 
            email=email, type='user', 
            status='valid', 
            phone=country_code+phone, 
            auth_user=auth_user, 
            user_subscription=user_subscription)
        
        service.sendinblue.contact.create(email=email,first_name=first_name, last_name=last_name)
        service.sendinblue.transaction_email.RegistraionConfirmationEmail(first_name, email, password, to=email, cc="lss@algotech.app", country=country).send()
        service.sendinblue.transaction_email.AccountActivationEmail(first_name, subscription_type, email, password, to=email, cc="lss@algotech.app", country=country).send()

        return Response("ok", status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'send/email/webhook', permission_classes=())
    @api_error_handler
    def handle_new_registeration_from_hubspot(self, request):

        Verify.is_hubspot_signature_valid(request)

        template_id, params_key = lib.util.getter.getparams(request,('template_id','params_key'),with_user=False)

        params_key=params_key.split(',') if type(params_key) is str else ()

        params_value = \
            lib.util.getter.getproperties(request.data.get('properties'), tuple(params_key), nest_property='value')

        params={params_key[i]:params_value[i] for i in range(len(params_key))}

        service.sendinblue.transaction_email.TransactionEmail(
            to=request.data.get('properties',{}).get('email',{}).get('value'), 
            template_id=template_id, 
            params=params).send()

        return Response("ok", status=status.HTTP_200_OK)