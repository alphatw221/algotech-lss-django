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
    def adjust_wallet(cls, wallet, transaction_created_after = None):

        _, total_used, total_expired = database.lss.point_transaction.get_earned_used_expired_points_sum(wallet.buyer.id, wallet.user_subscription.id, point_transaction_created_after = transaction_created_after)

        points_expired = max(total_expired-total_used ,0)
        wallet.points = max(wallet.points-points_expired ,0)
        wallet.save()

        database.lss.point_transaction.mark_transaction_points_used_calculated(wallet.buyer.id, start_from = transaction_created_after)
        database.lss.point_transaction.mark_transaction_point_expired_calculated(wallet.buyer.id, start_from = transaction_created_after)

    @classmethod
    def adjust_all_wallet_with_expired_points(cls, start_from=None, end_at=None):

        wallet_data = database.lss.point_transaction.get_wallet_data_with_expired_points(start_from, end_at)

        for _wallet_data in wallet_data:
            
            wallet = models.user.buyer_wallet.BuyerWallet.objects.get(
                user_subscription_id=_wallet_data.get('user_subscription_id'), 
                buyer_id = _wallet_data.get('buyer_id')
            )

            cls.adjust_wallet(wallet, _wallet_data.get('expired_points_transaction_created_at'))