import os

import django

from django.conf import settings


from api import models


import lib
import database
import traceback

from datetime import datetime

class WalletHelper():

    @classmethod
    def adjust_wallet(wallet, start_from=None, end_at=None):

        filter_data = {
            "created_at__gt":start_from,
            "created_at__lt":end_at
        }
        orders = wallet.buyer.orders.filter(**filter_data)

