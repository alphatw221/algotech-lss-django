import os
import config
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception as e:
    pass

from api import models

import traceback
import database
import service
from openpyxl import load_workbook
from io import BytesIO
import lib



def imoprt_account_job(file, room_id):
    try:
        workbook = load_workbook(filename=BytesIO(file.read()))

        worksheet = workbook.worksheets[0]

        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            cols = list(row)

            country = cols[0].value
            subscription_plan = cols[1].value
            name = cols[2].value
            email = cols[3].value
            password = cols[4].value
            signup_date = cols[5].value
            contact = cols[6].value




            country_code = business_policy.subscription.COUNTRY_SG if country_code in ['', 'undefined', 'null', None] else country_code

            # last_five_digit, image, bank_name, account_name, email, password, plan, period = lib.util.getter.getdata(request,("last_five_digit", "image", "bank_name", "account_name", "email", "password", "plan", "period"), required=True)
            # firstName, lastName, contactNumber, country, promoCode, timezone = lib.util.getter.getdata(request, ("firstName", "lastName", "contactNumber", "country", "promoCode", "timezone"), required=False)

            try:
                country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country_code)
                subscription_plan = country_plan.get_plan(plan)

                # kwargs={'email':email,'plan':plan,'period':period, 'promoCode':promoCode, 'country_plan':country_plan, 'subscription_plan':subscription_plan}

                # kwargs=rule.rule_checker.user_rule_checker.RegistrationRequireRefundChecker.check(**kwargs)
            except Exception:
                raise lib.error_handle.error.api_error.ApiVerifyError('support_for_refunding')
            # email = kwargs.get('email')
            # amount = kwargs.get('amount')

            # if image:
            #     image_name = image.name.replace(" ","")
            #     image_dir = f'register/receipt/{datetime.now().strftime("%Y/%m/%d,%H:%M:%S")}'
            #     image_url = lib.util.storage.upload_image(image_dir, image_name, image)

            # subscription_meta = {"last_five_digit":last_five_digit, 'bank_name':bank_name, "account_name": account_name, "receipt":image_url}

            ret = lib.helper.register_helper.create_new_register_account(plan, country_plan, subscription_plan, timezone, period, firstName, lastName, email, password, country, country_code,  contactNumber,  amount, subscription_meta=subscription_meta)












            print(country)
            print(subscription_plan)


        service.channels.account_import.send_result_data(room_id,{'result':'test'})
    except Exception:
        print(traceback.format_exc())
        service.channels.account_import.send_result_data(room_id,{'result':'test'})

  
