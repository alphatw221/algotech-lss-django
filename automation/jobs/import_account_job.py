import os
import config
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception as e:
    pass

from django.conf import settings
from api import models

import traceback
import database
import service
from openpyxl import load_workbook
from io import BytesIO
import lib
from datetime import datetime
import business_policy

def imoprt_account_job(file, room_id):
    try:
        workbook = load_workbook(filename=BytesIO(file.read()))

        worksheet = workbook.worksheets[0]

        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            try:
                cols = list(row)

                country_code = cols[0].value
                if country_code not in business_policy.subscription_plan.SubscriptionPlan.support_country:
                    raise ''
                subscription_plan = cols[1].value
                if subscription_plan not in business_policy.subscription_plan.SubscriptionPlan.support_plan:
                    raise ''
                username = cols[2].value
                email = cols[3].value
                password = str(cols[4].value)
                signup_date = cols[5].value if type(cols[5].value) == datetime else datetime.strptime(str(cols[5].value), '%Y-%m-%d')
                contactNumber = cols[6].value

                ret = lib.helper.register_helper.create_new_account_for_james(
                    country_code=country_code, 
                    usbscription_plan=subscription_plan, 
                    username=username, 
                    email=email, 
                    password=password, 
                    signup_date=signup_date, 
                    contactNumber=contactNumber
                    )

                service.channels.account_import.send_success_data(room_id,ret)
            except Exception:
                print(traceback.format_exc())
                service.channels.account_import.send_error_data(room_id,{'detail':'error'})
    except Exception:
        print(traceback.format_exc())
        service.channels.account_import.send_complete_data(room_id,{'detail':'ok'})

  
