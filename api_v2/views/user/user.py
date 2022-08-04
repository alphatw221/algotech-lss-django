
from django.contrib.auth.models import User as AuthUser
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from api import models
from api import rule

from automation import jobs

import service
import lib
import business_policy
from backend.i18n.email.subject import i18n_get_reset_password_success_mail_subject, i18n_get_reset_password_mail_subject #temp

from datetime import datetime, timedelta
import pytz


class UserViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = models.user.user.User.objects.all().order_by('id')
    serializer_class = models.user.user.UserSerializer
    filterset_fields = []

#-----------------------------------------admin----------------------------------------------------------------------------------------------



#-----------------------------------------buyer----------------------------------------------------------------------------------------------

    @action(detail=False, methods=['POST'], url_path=r'buyer/login/facebook', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_login_with_facebook(self, request):
        token = lib.helper.login_helper.FacebookLogin.get_token(request.data.get('facebook_token'),user_type='customer')
        return Response(token, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'buyer/login/google', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_login_with_google(self, request):

        token = lib.helper.login_helper.GoogleLogin.get_token(token=request.data.get('google_token'),user_type='customer')
        return Response(token, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer/account', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_get_account_info(self, request):
        api_user = lib.util.verify.Verify.get_customer_user(request)
        return Response(models.user.user.UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK)    

#-----------------------------------------seller----------------------------------------------------------------------------------------------
    
    @action(detail=False, methods=['POST'], url_path=r'seller/login/facebook', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_login_with_facebook(self, request):
        token = lib.helper.login_helper.FacebookLogin.get_token(request.data.get('facebook_token'),user_type='user')
        return Response(token, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'seller/login/general', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_general_login(self, request):
        email, password = lib.util.getter.getdata(request, ("email","password",), required=True)
        token = lib.helper.login_helper.GeneralLogin.get_token(email, password)
        if not token:
            Response({"message": "email or password incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(token, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'seller/login/google', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_login_with_google(self, request):

        token = lib.helper.login_helper.GoogleLogin.get_token(token=request.data.get('google_token'),user_type='user')
        return Response(token, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller/account', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_get_account_info(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        return Response(models.user.user.UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK) 

    
    @action(detail=False, methods=['PUT'], url_path=r'seller/language/(?P<language>[^/.]+)', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_change_language(self, request, language):
        api_user = lib.util.verify.Verify.get_seller_user(request)

        if language not in [business_policy.subscription.LANGUAGE_ENGLICH,
                            business_policy.subscription.LANGUAGE_INDONESIAN,
                            business_policy.subscription.LANGUAGE_SIMPLIFY_CHINESE,
                            business_policy.subscription.LANGUAGE_TRANDITIONAL_CHINESE]:
            raise lib.error_handle.error.api_error.ApiCallerError('language not supported')

        api_user.lang = language
        api_user.save()

        return Response( models.user.user.UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'seller/password/change', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_change_password(self, request):
        password, new_password = lib.util.getter.getdata(request, ("password", "new_password"), required=True)
        auth_user = request.user
        
        if not auth_user.check_password(password):
            return Response({"message": "password incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        rule.rule_checker.user_rule_checker.SellerChangePasswordRuleChecker.check(**{"password":password,"new_password":new_password})

        auth_user.set_password(new_password)
        auth_user.save()

        return Response({"message":"complete"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'seller/password/reset')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_reset_password(self, request):
        
        # return Response({
        #     "Customer Name":'MyName',
        #     "Email":"alphatw22193@gmailc.om",
        #     "New Password":"1234*****"
        # }, status=status.HTTP_200_OK)
        code, new_password = lib.util.getter.getdata(request, ( "code", "new_password"), required=True)

        rule.rule_checker.user_rule_checker.SellerResetPasswordRuleChecker.check(**{"new_password":new_password})
        ret = lib.code_manager.password_code_manager.PasswordResetCodeManager.execute(code, new_password)
        
        email = ret["Email"]
        auth_user = AuthUser.objects.get(email=email)
        
        api_user = models.user.user.User.objects.get(email=email,type='user')
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        service.email.email_service.EmailService.send_email_template(
            jobs.send_email_job.send_email_job,
            i18n_get_reset_password_success_mail_subject(lang=user_subscription.lang),
            email,
            "reset_password_success_email.html",
            {"email":email,"username":auth_user.username},
            lang=user_subscription.lang
        )
        
        return Response(ret, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'seller/password/forgot')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_forgot_password(self, request):
        email, = lib.util.getter.getdata(request, ("email",), required=True)
        email = email.lower() #TODO add in checkrule
        email = email.replace(" ", "") #TODO add in checkrule

        if not AuthUser.objects.filter(email=email).exists() or not models.user.user.User.objects.filter(email=email,type='user').exists():
            raise lib.error_handle.error.api_error.ApiVerifyError('The account doesn’t exist')

        auth_user = AuthUser.objects.get(email=email)
        api_user = models.user.user.User.objects.get(email=email,type='user')
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        code = lib.code_manager.password_code_manager.PasswordResetCodeManager.generate(auth_user.id,user_subscription.lang)
        service.email.email_service.EmailService.send_email_template(
            jobs.send_email_job.send_email_job,
            i18n_get_reset_password_mail_subject(lang=user_subscription.lang),
            email,
            "email_reset_password_link.html",
            {"url":settings.GCP_API_LOADBALANCER_URL +"/seller/password/reset","code":code,"username":auth_user.username},
            lang=user_subscription.lang)

        return Response({"message":"The email has been sent. If you haven't received the email after a few minutes, please check your spam folder. "}, status=status.HTTP_200_OK)





    @action(detail=False, methods=['POST'], url_path=r'register/validate/(?P<country_code>[^/.]+)', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def validate_register_data(self, request, country_code):
        email, plan, period = lib.util.getter.getdata(request, ("email", "plan", "period"), required=True)
        promoCode, = lib.util.getter.getdata(request, ("promoCode",), required=False)

        country_code = business_policy.subscription.COUNTRY_SG if country_code in ['', 'undefined', 'null', None] else country_code
        country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country_code)
        subscription_plan = country_plan.get_plan(plan)

        kwargs = {'email':email, 'plan':plan, 'period':period, 'promoCode':promoCode, 'country_plan':country_plan, 'subscription_plan':subscription_plan}
        kwargs = rule.rule_checker.user_rule_checker.RegistrationDataRuleChecker.check(**kwargs)

        email = kwargs.get('email')
        amount = kwargs.get('amount')
        marketing_plans = kwargs.get('marketing_plans')

        intent = service.stripe.stripe.create_payment_intent(settings.STRIPE_API_KEY, amount, country_plan.currency, email)
        if not intent:
            raise lib.error_handle.error.api_error.ApiCallerError("invalid email")

        return Response({
            "client_secret":intent.client_secret,
            "payment_amount":amount,
            "user_plan":plan,
            "period":period,
            "currency":country_plan.currency,
            "marketing_plans":marketing_plans
        }, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'register/(?P<country_code>[^/.]+)/stripe', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def user_register_with_stripe(self, request, country_code):
        country_code = business_policy.subscription.COUNTRY_SG if country_code in ['', 'undefined', 'null', None] else country_code
        email, password, plan, period, intentSecret = lib.util.getter.getdata(request,("email", "password", "plan", "period", "intentSecret"),required=True)
        firstName, lastName, contactNumber, country, promoCode, timezone = lib.util.getter.getdata(request, ("firstName", "lastName", "contactNumber", "country", "promoCode", "timezone"), required=False)

        payment_intent_id = intentSecret[:27]

        paymentIntent = service.stripe.stripe.retrieve_payment_intent(settings.STRIPE_API_KEY, payment_intent_id)
        if not paymentIntent:
            raise lib.error_handle.error.api_error.ApiCallerError("payment error, please contact support team")
        kwargs = {'paymentIntent':paymentIntent,'email':email,'plan':plan,'period':period, 'promoCode':promoCode}
        kwargs=rule.rule_checker.user_rule_checker.RegistrationPaymentCompleteChecker.check(**kwargs)

        try:
            country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country_code)
            subscription_plan = country_plan.get_plan(plan)

            kwargs.update({'country_plan':country_plan, 'subscription_plan':subscription_plan})
            kwargs=rule.rule_checker.user_rule_checker.RegistrationRequireRefundChecker.check(**kwargs)
        except Exception:
            #TODO refund
            raise lib.error_handle.error.api_error.ApiVerifyError('data invalid, please contact support for refunding')

        email = kwargs.get('email')
        amount = kwargs.get('amount')

        subscription_meta={"stripe payment intent":intentSecret}
        ret = lib.helper.register_helper.create_new_register_account(plan, country_plan, subscription_plan, timezone, period, firstName, lastName, email, password, country, country_code,  contactNumber,  amount, paymentIntent, subscription_meta=subscription_meta)

        return Response(ret, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'register/(?P<country_code>[^/.]+)/transfer', permission_classes=(), parser_classes=(MultiPartParser,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def user_register_with_bank_transfer(self, request, country_code):
        country_code = business_policy.subscription.COUNTRY_SG if country_code in ['', 'undefined', 'null', None] else country_code
        last_five_digit, image, account_name, email, password, plan, period = lib.util.getter.getdata(request,("last_five_digit", "image", "account_name", "email", "password", "plan", "period"), required=True)
        firstName, lastName, contactNumber, country, promoCode, timezone = lib.util.getter.getdata(request, ("firstName", "lastName", "contactNumber", "country", "promoCode", "timezone"), required=False)

        try:
            country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country_code)
            subscription_plan = country_plan.get_plan(plan)

            kwargs={'email':email,'plan':plan,'period':period, 'promoCode':promoCode, 'country_plan':country_plan, 'subscription_plan':subscription_plan}

            kwargs=rule.rule_checker.user_rule_checker.RegistrationRequireRefundChecker.check(**kwargs)
        except Exception:
            raise lib.error_handle.error.api_error.ApiVerifyError('data invalid, please contact support for refunding')
        email = kwargs.get('email')
        amount = kwargs.get('amount')

        if image:
            image_path = default_storage.save(f'register/receipt/{datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}/{image.name}', ContentFile(image.read()))

        subscription_meta = {"last_five_digit":last_five_digit, "account_name": account_name, "receipt":image_path}

        ret = lib.helper.register_helper.create_new_register_account(plan, country_plan, subscription_plan, timezone, period, firstName, lastName, email, password, country, country_code,  contactNumber,  amount, subscription_meta=subscription_meta)

        return Response(ret, status=status.HTTP_200_OK)