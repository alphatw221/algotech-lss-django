from django.contrib.auth.models import User as AuthUser

from api import models
import lib
import service
import business_policy

from datetime import datetime, timedelta
import pytz






def create_account_with_user_register(user_register):


    country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(user_register.country)

    now = datetime.now()
    expired_at = now+timedelta(days=90) if user_register.period == business_policy.subscription.PERIOD_QUARTER else now+timedelta(days=365)
    
    auth_user = AuthUser.objects.create_user(
        username=user_register.name, email=user_register.email, password=user_register.password)

    user_subscription = models.user.user_subscription.UserSubscription.objects.create(
        name=user_register.name, 
        status=models.user.user_subscription.STATUS_VALID, 
        started_at=now,
        expired_at=expired_at, 
        user_plan= {"activated_platform" : [models.user.user_subscription.PLATFORM_FACEBOOK,models.user.user_subscription.PLATFORM_YOUTUBE,models.user.user_subscription.PLATFORM_INSTAGRAM]}, 
        meta_country={ 'activated_country': [user_register.country] },
        type=user_register.type,
        lang=country_plan.language,
        country = user_register.country,
        purchase_price = user_register.payment_amount,
        **business_policy.subscription_plan.SubscriptionPlan.get_plan_limit(user_register.type)
        )
        
    api_user = models.user.user.User.objects.create(
        name=user_register.name, email=user_register.email, type=models.user.user.TYPE_SELLER, status=models.user.user.STATUS_VALID, phone=user_register.phone, auth_user=auth_user, user_subscription=user_subscription)
    
    models.user.deal.Deal.objects.create(
        user_subscription=user_subscription,
        purchased_plan=user_register.type, 
        total=user_register.payment_amount, 
        status=models.user.deal.STATUS_SUCCESS, 
        payer=api_user, 
        payment_time=datetime.utcnow()
    )

    
    lib.util.marking_tool.NewUserMark.mark(api_user, save = True)





def create_new_register_account(plan, country_plan, subscription_plan, timezone, period, firstName, lastName, email, password, country, country_code,  contactNumber,  amount, paymentIntent=None, subscription_meta:dict={}):


    now = datetime.now(pytz.timezone(timezone)) if timezone in pytz.common_timezones else datetime.now()
    expired_at = now+timedelta(days=90) if period == business_policy.subscription.PERIOD_QUARTER else now+timedelta(days=365)
    
    auth_user = AuthUser.objects.create_user(
        username=f'{firstName} {lastName}', email=email, password=password)

    user_subscription = models.user.user_subscription.UserSubscription.objects.create(
        name=f'{firstName} {lastName}', 
        status='valid', 
        started_at=now,
        expired_at=expired_at, 
        user_plan= {"activated_platform" : ["facebook","youtube","instagram"]}, 
        meta_country={ 'activated_country': [country_code] },
        meta = subscription_meta,
        type=plan,
        lang=country_plan.language,
        country = country_code,
        purchase_price = amount,
        **business_policy.subscription_plan.SubscriptionPlan.get_plan_limit(plan)
        )
        
    api_user = models.user.user.User.objects.create(
        name=f'{firstName} {lastName}', email=email, type='user', status='valid', phone=contactNumber, auth_user=auth_user, user_subscription=user_subscription)
    
    models.user.deal.Deal.objects.create(
        user_subscription=user_subscription,
        purchased_plan=plan, 
        total=amount, 
        status=models.user.deal.STATUS_SUCCESS, 
        payer=api_user, 
        payment_time=datetime.utcnow()
    )

    
    lib.util.marking_tool.NewUserMark.mark(api_user, save = True)
    
    # marketing_plans = kwargs.get('marketing_plans')

    # for key, val in marketing_plans.items():
    #     if key == "welcome_gift":
    #         lib.util.marking_tool.WelcomeGiftUsedMark.mark(api_user, save = True)
    #         PromotionCode.objects.create(
    #             name=key,
    #             api_user=api_user,
    #             user_subscription=user_subscription,
    #             used_at=datetime.utcnow(),
    #             deal=deal_obj
    #         )

    service.sendinblue.contact.create(email=email,first_name=firstName, last_name=lastName)
    service.hubspot.contact.create(email=email, 
        first_name=firstName, 
        last_name=lastName,
        subscription_type=plan, 
        subscription_status="new",
        country=country_code,
        expiry_date=int(expired_at.replace(hour=0,minute=0,second=0,microsecond=0).timestamp()*1000)
    )
    
    service.sendinblue.transaction_email.AccountActivationEmail(firstName, plan, email, password, to=[email], cc=country_plan.cc, country=country_code).send()
    
    return {
        "Customer Name":f'{firstName} {lastName}',
        "Email":email,
        "Password":password[:4]+"*"*(len(password)-4),
        "Target Country":country, 
        "Your Plan":subscription_plan.get('text'),
        "Subscription Period":"Monthly",
        "Subscription End Date":expired_at.strftime("%d %B %Y %H:%M"),
        "Receipt":paymentIntent.charges.get('data')[0].get('receipt_url') if paymentIntent else ""
    }


def create_user_register(plan, timezone, period, firstName, lastName, email, password, country, country_code,  contactNumber ):


    now = datetime.now(pytz.timezone(timezone)) if timezone in pytz.common_timezones else datetime.now()
    # expired_at = now+timedelta(days=90) if period == business_policy.subscription.PERIOD_QUARTER else now+timedelta(days=365)
    
    # auth_user = AuthUser.objects.create_user(
    #     username=f'{firstName} {lastName}', email=email, password=password)

    # user_subscription = models.user.user_subscription.UserSubscription.objects.create(
    #     name=f'{firstName} {lastName}', 
    #     status='valid', 
    #     started_at=now,
    #     expired_at=expired_at, 
    #     user_plan= {"activated_platform" : ["facebook","youtube","instagram"]}, 
    #     meta_country={ 'activated_country': [country_code] },
    #     meta = subscription_meta,
    #     type=plan,
    #     lang=country_plan.language,
    #     country = country_code,
    #     purchase_price = amount,
    #     **business_policy.subscription_plan.SubscriptionPlan.get_plan_limit(plan)
    #     )
    user_register = models.user.user_register.UserRegister.objects.create(
        name=f'{firstName} {lastName}',
        password=password,
        email=email,
        phone=contactNumber,
        period=period,
        timezone=timezone,
        created_at=now,
        type=plan,
        country=country_code,
        target_country=country
    )