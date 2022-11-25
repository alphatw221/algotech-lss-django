import os

import django

from django.conf import settings


from api import models


import lib
import database
import traceback

from datetime import datetime
import database

class WalletHelper():

    @classmethod
    def adjust_wallet(cls, wallet, order_created_after = None):

        _, total_used, total_expired = database.lss.order.get_total_earned_used_expired_points(wallet.buyer.id, wallet.user_subscription.id, order_created_after = order_created_after)

        points_expired = max(total_expired-total_used,0)
        wallet.points = max(wallet.points-points_expired,0)
        wallet.save()

    @classmethod
    def adjust_all_wallet_with_expired_points(cls, start_from=None, end_at=None):

        wallet_data = database.lss.order.get_wallet_data_with_expired_points(start_from, end_at)

        for _wallet_data in wallet_data:
            wallet = models.user.buyer_wallet.BuyerWallet.objects.get(**_wallet_data)
            cls.adjust_wallet(wallet, wallet_data.get('created_at'))