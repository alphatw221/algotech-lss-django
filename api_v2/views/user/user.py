
from django.contrib.auth.models import User as AuthUser
from django.conf import settings
from django.core.files.base import ContentFile
from lib.util import verify

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import StaticHTMLRenderer

from api import models
from api import rule
from api.models.user import user_register

from automation import jobs
import database

import service
import lib
import business_policy
from backend.i18n.email.subject import i18n_get_reset_password_success_mail_subject, i18n_get_reset_password_mail_subject #temp

from datetime import datetime, timedelta
import pytz
import random
import string

#------------------------------------------------------------------------------------------
class UserSubscriptionAccountInfo(models.user.user_subscription.UserSubscriptionSerializer):

    facebook_pages = models.facebook.facebook_page.FacebookPageInfoSerializer(
        many=True, read_only=True, default=list)
    instagram_profiles = models.instagram.instagram_profile.InstagramProfileInfoSerializer(
        many=True, read_only=True, default=list)
    youtube_channels = models.youtube.youtube_channel.YoutubeChannelInfoSerializer(
        many=True, read_only=True, default=list)
    twitch_channels = models.twitch.twitch_channel.TwitchChannelInfoSerializer(
        many=True, read_only=True, default=list)
    tiktok_accounts = models.tiktok.tiktok_account.TikTokAccountInfoSerializer(
        many=True, read_only=True, default=list)
    product_categories = models.product.product_category.ProductCategorySerializer(
        many=True, read_only=True, default=list)
class UserSerializerSellerAccountInfo(models.user.user.UserSerializer):
    user_subscription = UserSubscriptionAccountInfo(read_only=True, default=dict)
#------------------------------------------------------------------------------------------
class UserSubscriptionSerializerName(models.user.user_subscription.UserSubscriptionSerializer):
    class Meta:
        model = models.user.user_subscription.UserSubscription
        fields = ['name']
class WalletSerializerWithSellerInfo(models.user.buyer_wallet.BuyerWalletSerializer):
    user_subscription = UserSubscriptionSerializerName(read_only=True, default=dict)
class UserSerializerBuyerAccountInfo(models.user.user.UserSerializer):
    wallets = WalletSerializerWithSellerInfo(many=True, read_only=True, default=list)
#------------------------------------------------------------------------------------------

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.user.user.User.objects.all().order_by('id')
    serializer_class = models.user.user.UserSerializer
    filterset_fields = []

# #-----------------------------------------admin----------------------------------------------------------------------------------------------

#     @action(detail=False, methods=['GET'], url_path=r'dealer/search/list', permission_classes=(IsAuthenticated,))
#     @lib.error_handle.error_handler.api_error_handler.api_error_handler
#     def user_list_from_dealer(self, request):
#         api_user = lib.util.verify.Verify.get_seller_user(request)
#         dealer_user_subscription = lib.util.verify.Verify.get_dealer_user_subscription_from_api_user(api_user)
#         data = database.lss.dealer.get_seller_info_from_dealer(dealer_user_subscription.id)

#         return Response(data, status=status.HTTP_200_OK)

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
        return Response(UserSerializerBuyerAccountInfo(api_user).data, status=status.HTTP_200_OK)    

#-----------------------------------------Dealer----------------------------------------------------------------------------------------------

    # @action(detail=False, methods=['POST'], url_path=r'dealer/login', permission_classes=(IsAdminUser,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def dealer_login(self, request):
    #     email, password = lib.util.getter.getdata(request, ("email","password",), required=True)
    #     api_user = lib.util.verify.Verify.get_customer_user(request)
    #     dealer_user_subscription = lib.util.verify.Verify.get_dealer_user_subscription_from_api_user(api_user)
    #     if not dealer_user_subscription:
    #         return Response({"message":"not_dealer_account"}, status=status.HTTP_401_UNAUTHORIZED)
    #     token = lib.helper.login_helper.GeneralLogin.get_token(email, password)
    #     if not token:
    #         return Response({"message":"email_or_password_incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
    #     return Response(token, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['POST'], url_path=r'dealer/verify_code')
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def dealer_verify_code(self, request):
    #     email, = lib.util.getter.getdata(request, ("user_email",), required=True)
    #     api_user = models.user.user.User.objects.get(email=email,type='user')
    #     code = string.digits
    #     code = ''.join(random.choice(code) for i in range(4))

    #     jobs.send_email_job.send_email_job(i18n_get_verify_code_subject(lang=api_user.lang),email, 'email_verification_code.html', parameters={"verify_code":code}, lang=api_user.lang)

    #     return Response(code, status=status.HTTP_200_OK)

#-----------------------------------------Admin----------------------------------------------------------------------------------------------

    @action(detail=False, methods=['POST'], url_path=r'admin/login', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def admin_login(self, request):
        from lss.views.custom_jwt import CustomTokenObtainPairSerializer

        email, password = lib.util.getter.getdata(request, ("email","password",), required=True)
        # token = lib.helper.login_helper.GeneralLogin.get_token(email, password)
        # if not token:
        #     return Response({"message":"email_or_password_incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        # code = string.digits
        # code = ''.join(random.choice(code) for i in range(4))

        # api_user = models.user.user.User.objects.get(email=email,type='user')

        # jobs.send_email_job.send_email_job( lib.i18n.veification_code_email.i18n_get_notify_wishlist_subject(lang=api_user.lang),email, 'email_verification_code.html', parameters={"verify_code":code}, lang=api_user.lang)
        if not AuthUser.objects.filter(email=email).exists():
            return Response({"message":"email_or_password_incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        auth_user = AuthUser.objects.get(email=email)
        if not auth_user.check_password(password):
            return Response({"message":"email_or_password_incorrect"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_email': email
        } , status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'admin/account', permission_classes=(IsAdminUser,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def admin_get_account_info(self, request):
        return Response(models.user.user.AuthUserSerializer(request.user).data, status=status.HTTP_200_OK) 

    @action(detail=False, methods=['POST'], url_path=r'admin/import', permission_classes=(IsAdminUser,), parser_classes=(MultiPartParser,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def admin_import_account(self, request):
        # service.rq.queue.enqueue_test_queue(jobs.import_account_job.imoprt_account_job, file=request.data.get('file'), room_id = request.data.get('room_id'))

        service.rq.queue.enqueue_general_queue(jobs.import_account_job.imoprt_account_job,file=request.data.get('file'), room_id = request.data.get('room_id'))
        return Response('ok', status=status.HTTP_200_OK) 
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
            return Response({"message":"email_or_password_incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
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
        return Response(UserSerializerSellerAccountInfo(api_user).data, status=status.HTTP_200_OK) 

    
    # not use for now
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

        return Response(UserSerializerSellerAccountInfo(api_user).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'seller/password/change', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_change_password(self, request):
        password, new_password = lib.util.getter.getdata(request, ("password", "new_password"), required=True)
        auth_user = request.user
        
        if not auth_user.check_password(password):
            raise lib.error_handle.error.api_error.ApiVerifyError("password_incorrect")
        rule.rule_checker.user_rule_checker.SellerChangePasswordRuleChecker.check(**{"password":password,"new_password":new_password})

        auth_user.set_password(new_password)
        auth_user.save()

        return Response({"message":"complete"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'seller/password/reset', permission_classes=())
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
        
        email = ret["email"]
        auth_user = AuthUser.objects.get(email=email)
        
        api_user = models.user.user.User.objects.get(email=email,type='user')
        # user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        jobs.send_email_job.send_email_job(
            i18n_get_reset_password_success_mail_subject(lang=api_user.lang),
            email,
            "reset_password_success_email.html",
            {"email":email,"username":auth_user.username},
            lang=api_user.lang
        )
        # service.email.email_service.EmailService.send_email_template(
        #     jobs.send_email_job.send_email_job,
        #     i18n_get_reset_password_success_mail_subject(lang=api_user.lang),
        #     email,
        #     "reset_password_success_email.html",
        #     {"email":email,"username":auth_user.username},
        #     lang=api_user.lang
        # )
        
        return Response(ret, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'seller/password/forgot', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_forgot_password(self, request):
        email, = lib.util.getter.getdata(request, ("email",), required=True)
        email = email.lower() #TODO add in checkrule
        email = email.replace(" ", "") #TODO add in checkrule

        if not AuthUser.objects.filter(email=email).exists() or not models.user.user.User.objects.filter(email=email,type='user').exists():
            raise lib.error_handle.error.api_error.ApiVerifyError('account_not_exist')

        auth_user = AuthUser.objects.get(email=email)
        api_user = models.user.user.User.objects.get(email=email,type='user')
        # user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        code = lib.code_manager.password_code_manager.PasswordResetCodeManager.generate(auth_user.id,api_user.lang)
        
        jobs.send_email_job.send_email_job(
            subject=i18n_get_reset_password_mail_subject(lang=api_user.lang),
            email=email,
            template="email_reset_password_link.html",
            parameters={"url":settings.GCP_API_LOADBALANCER_URL +"/seller/web/password/reset","code":code,"username":auth_user.username},
            lang=api_user.lang,
            )
        # service.email.email_service.EmailService.send_email_template(
        #     jobs.send_email_job.send_email_job,
        #     i18n_get_reset_password_mail_subject(lang=api_user.lang),
        #     email,
        #     "email_reset_password_link.html",
        #     {"url":settings.GCP_API_LOADBALANCER_URL +"/seller/web/password/reset","code":code,"username":auth_user.username},
        #     lang=api_user.lang)

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
            raise lib.error_handle.error.api_error.ApiCallerError("invalid_email")

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
            raise lib.error_handle.error.api_error.ApiCallerError("payment_error")
        kwargs = {'paymentIntent':paymentIntent,'email':email,'plan':plan,'period':period, 'promoCode':promoCode}
        kwargs=rule.rule_checker.user_rule_checker.RegistrationPaymentCompleteChecker.check(**kwargs)

        try:
            country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country_code)
            subscription_plan = country_plan.get_plan(plan)

            kwargs.update({'country_plan':country_plan, 'subscription_plan':subscription_plan})
            kwargs=rule.rule_checker.user_rule_checker.RegistrationRequireRefundChecker.check(**kwargs)
        except Exception:
            #TODO refund
            raise lib.error_handle.error.api_error.ApiVerifyError('support_for_refunding')

        email = kwargs.get('email')
        amount = kwargs.get('amount')

        subscription_meta={"stripe payment intent":intentSecret}
        ret = lib.helper.register_helper.create_new_register_account(plan, country_plan, subscription_plan, timezone, period, firstName, lastName, email, password, country, country_code,  contactNumber,  amount, paymentIntent, subscription_meta=subscription_meta)

        return Response(ret, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'register/(?P<country_code>[^/.]+)/transfer', permission_classes=(), parser_classes=(MultiPartParser,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def user_register_with_bank_transfer(self, request, country_code):
        country_code = business_policy.subscription.COUNTRY_SG if country_code in ['', 'undefined', 'null', None] else country_code

        last_five_digit, image, bank_name, account_name, email, password, plan, period = lib.util.getter.getdata(request,("last_five_digit", "image", "bank_name", "account_name", "email", "password", "plan", "period"), required=True)
        firstName, lastName, contactNumber, country, promoCode, timezone = lib.util.getter.getdata(request, ("firstName", "lastName", "contactNumber", "country", "promoCode", "timezone"), required=False)

        try:
            country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country_code)
            subscription_plan = country_plan.get_plan(plan)

            kwargs={'email':email,'plan':plan,'period':period, 'promoCode':promoCode, 'country_plan':country_plan, 'subscription_plan':subscription_plan}

            kwargs=rule.rule_checker.user_rule_checker.RegistrationRequireRefundChecker.check(**kwargs)
        except Exception:
            raise lib.error_handle.error.api_error.ApiVerifyError('support_for_refunding')
        email = kwargs.get('email')
        amount = kwargs.get('amount')

        if image:
            image_name = image.name.replace(" ","")
            image_dir = f'register/receipt/{datetime.now().strftime("%Y/%m/%d,%H:%M:%S")}'
            image_url = lib.util.storage.upload_image(image_dir, image_name, image)

        subscription_meta = {"last_five_digit":last_five_digit, 'bank_name':bank_name, "account_name": account_name, "receipt":image_url}

        ret = lib.helper.register_helper.create_new_register_account(plan, country_plan, subscription_plan, timezone, period, firstName, lastName, email, password, country, country_code,  contactNumber,  amount, subscription_meta=subscription_meta)

        return Response(ret, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'register/(?P<country_code>[^/.]+)')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def user_register_with_ecpay(self, request, country_code):

        email, password, plan, period = lib.util.getter.getdata(request,("email", "password", "plan", "period"), required=True)
        firstName, lastName, contactNumber, country, promoCode, timezone = lib.util.getter.getdata(request, ("firstName", "lastName", "contactNumber", "country", "promoCode", "timezone"), required=False)
        country_code = business_policy.subscription.COUNTRY_SG if country_code in ['', 'undefined', 'null', None] else country_code

        country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country_code)
        subscription_plan = country_plan.get_plan(plan)

        kwargs={'email':email,'plan':plan,'period':period, 'promoCode':promoCode, 'country_plan':country_plan, 'subscription_plan':subscription_plan}
        kwargs=rule.rule_checker.user_rule_checker.RegistrationDataRuleChecker.check(**kwargs)
        email = kwargs.get('email')
        amount = kwargs.get('amount')

        user_register = models.user.user_register.UserRegister.objects.create(
            name=f'{firstName} {lastName}',
            password=password,
            email=email,
            phone=contactNumber,
            period=period,
            timezone=timezone,
            type=plan,
            country=country_code,
            target_country=country,
            payment_amount = amount
        )
        data = models.user.user_register.UserRegisterSerializer(user_register).data
        data['oid'] = database.lss.user_register.get_oid_by_id(user_register.id)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'register/(?P<user_register_oid>[^/.]+)/pay/ecpay')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def user_register_with_ecpay(self, request, user_register_oid):

        user_register = lib.util.verify.Verify.get_user_register_with_oid(user_register_oid)
        MERCHANT_ID = '2000132'
        HASH_KEY='5294y06JbISpM5x9'
        HASH_IV='v77hoKGq4kWxNNIS'    #put this to settings in the future
        
        success, url, params = service.ecpay.ecpay.create_register_order(MERCHANT_ID, HASH_KEY, HASH_IV, user_register.payment_amount , user_register.type, 
            f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/user/register/ecpay/callback/?oid={user_register_oid}', 
            f'https://liveshowseller.com/thank-you/',
        )
        
        if not success:
            raise lib.error_handle.error.api_error.ApiCallerError('please contact support team or try another payment method.')

        return Response({'url':url,'params':params}, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['POST'], url_path=r'register/(?P<country_code>[^/.]+)/ecpay')
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def user_register_with_ecpay(self, request, country_code):
    #     country_code = business_policy.subscription.COUNTRY_SG if country_code in ['', 'undefined', 'null', None] else country_code

    #     email, password, plan, period = lib.util.getter.getdata(request,("email", "password", "plan", "period"), required=True)
    #     firstName, lastName, contactNumber, country, promoCode, timezone = lib.util.getter.getdata(request, ("firstName", "lastName", "contactNumber", "country", "promoCode", "timezone"), required=False)

    #     try:
    #         country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country_code)
    #         subscription_plan = country_plan.get_plan(plan)

    #         kwargs={'email':email,'plan':plan,'period':period, 'promoCode':promoCode, 'country_plan':country_plan, 'subscription_plan':subscription_plan}

    #         kwargs=rule.rule_checker.user_rule_checker.RegistrationRequireRefundChecker.check(**kwargs)
    #     except Exception:
    #         raise lib.error_handle.error.api_error.ApiVerifyError('support_for_refunding')
    #     email = kwargs.get('email')
    #     amount = kwargs.get('amount')
        
    #     # just test: merchant_id ,hash_key ,hash_iv
    #     merchant_id='2000132'
    #     hash_key='5294y06JbISpM5x9'
    #     hash_iv='v77hoKGq4kWxNNIS'
        
    #     action,payment = service.ecpay.ecpay.create_register_order(merchant_id, hash_key, hash_iv, int(amount) , str(plan), 
    #         f'https://staginglss.accoladeglobal.net/api/v2/user/register/ecpay/callback/?email={email}', 
    #         f'https://liveshowseller.com/thank-you/',
    #     )
        
    #     # get_user_register = lib.util.verify.Verify.get_user_register_by_email(email)
    #     # user_register = models.user.user_register.UserRegisterSerializer(get_user_register).data
    #     # print(user_register['type'])
        
        
    #     lib.helper.register_helper.create_user_register(plan, timezone, period, firstName, lastName, email, password, country, country_code,  contactNumber)

    #     return Response({'action':action,'data':payment}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'register/ecpay/callback',parser_classes=(FormParser,), renderer_classes = (StaticHTMLRenderer,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def user_register_with_ecpay_callback(self, request):

        oid, = lib.util.getter.getparams(request, ('oid',), with_user=False)
        user_register = lib.util.verify.Verify.get_user_register_with_oid(oid)

        MERCHANT_ID = '2000132'
        HASH_KEY='5294y06JbISpM5x9'
        HASH_IV='v77hoKGq4kWxNNIS'
        
        params = request.data.dict()
        
        check_mac_value = service.ecpay.ecpay.check_mac_value(MERCHANT_ID, HASH_KEY, HASH_IV, params)
        
        if not params or params.get('CheckMacValue') != check_mac_value :
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid')

        if params.get('RtnCode') == '0':
            raise lib.error_handle.error.api_error.ApiVerifyError('fail')
        
        if params.get('amount') != user_register.payment_amount:
            user_register.status = models.user.user_register.STATUS_PENDING_REFUND
            user_register.save()
            raise lib.error_handle.error.api_error.ApiVerifyError('support_for_refunding')

        invoice = service.ecpay.ecpay.register_create_invoice(MERCHANT_ID, HASH_KEY, HASH_IV, user_register, user_register.payment_amount)

        user_register.meta['ecpay']={'InvoiceNumber':invoice['InvoiceNumber']}
        user_register.status = models.user.user_register.STATUS_COMPLETE
        user_register.save()

        lib.helper.register_helper.create_account_with_user_register(user_register)

        return Response('1|ok')