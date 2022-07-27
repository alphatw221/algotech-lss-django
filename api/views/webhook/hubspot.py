from django.conf import settings
from django.contrib.auth.models import User as AuthUser

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models.user.promotion_code import PromotionCode


from api.utils.common.verify import Verify
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.verify import ApiVerifyError
from api import models
from api import rule
from api.utils.orm.deal import record_subscription_for_trial_user
from business_policy.marketing_plan import MarketingPlan

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

        Verify.is_hubspot_signature_valid(request)
        vid, = lib.util.getter.getdata(request,('vid',)) 
        first_name, last_name, email, subscription_type, country_code, phone = \
            lib.util.getter.getproperties(request.data.get('properties'),('firstname','lastname','email','subscription_type','country_code','phone'), nest_property='value')

        country = lib.util.country_mapping.country_code_to_country.get(country_code,'SG')
        password = ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8))
        country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country)

        rule.check_rule.user_check_rule.UserCheckRule.has_email_been_registered_as_seller(email=email)

        now = datetime.now() 
        expired_at = now+timedelta(days=90)

        if AuthUser.objects.filter(email=email).exists():
            auth_user = AuthUser.objects.get(email=email)
            # set new password
            auth_user.set_password(password)
            auth_user.save()

        else:
            auth_user = AuthUser.objects.create_user(
                username=f'{first_name} {last_name}', email=email, password=password)
        
        user_subscription = models.user.user_subscription.UserSubscription.objects.create(
            name=f'{first_name} {last_name}', 
            status='new', 
            started_at=now,
            expired_at=expired_at, 
            user_plan= {"activated_platform" : ["facebook", "instagram"]}, 
            meta_country={ 'activated_country': [country] },
            type='trial',
            lang=country_plan.language ,
            country = country
            )
        
        api_user = models.user.user.User.objects.create(name=f'{first_name} {last_name}', 
            email=email, type='user', 
            status='valid', 
            phone=country_code+phone, 
            auth_user=auth_user, 
            user_subscription=user_subscription)
        
        record_subscription_for_trial_user(user_subscription, api_user)
        
        lib.util.marking_tool.NewUserMark.mark(api_user, save = True)
        marketing_plans = MarketingPlan.get_plans("current_plans")
        for key, val in marketing_plans.items():
            if key == "welcome_gift":
                lib.util.marking_tool.WelcomeGiftUsedMark.mark(api_user, save = True, mark_value=False)
                PromotionCode.objects.create(
                    name=key,
                    api_user=api_user,
                    user_subscription=user_subscription,
                )
        
        service.hubspot.contact.update(vid,expiry_date=int(expired_at.replace(hour=0,minute=0,second=0,microsecond=0).timestamp()*1000))
        service.sendinblue.contact.create(email=email,first_name=first_name, last_name=last_name)
        service.sendinblue.transaction_email.AccountActivationEmail(first_name, subscription_type, email, password, to=[email], cc=country_plan.cc, country=country).send()

        return Response("ok", status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'send/email/webhook', permission_classes=())
    @api_error_handler
    def send_email_webhook(self, request):

        Verify.is_hubspot_signature_valid(request)

        template_id, params_key = lib.util.getter.getparams(request,('template_id','params_key'),with_user=False)

        #TODO check template_id
        
        params_key=params_key.split(',') if type(params_key) is str else ()

        params_value = \
            lib.util.getter.getproperties(request.data.get('properties'), tuple(params_key), nest_property='value')

        params={params_key[i]:params_value[i] for i in range(len(params_key))}

        service.sendinblue.transaction_email.TransactionEmail(
            to=[request.data.get('properties',{}).get('email',{}).get('value')], 
            template_id=template_id, 
            params=params).send()

        return Response("ok", status=status.HTTP_200_OK)