from .default import DefaultCustomerImportProcessor
import lib
from api import models
import math
from datetime import datetime, timedelta

CONTENT_TYPE_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
CONTENT_TYPE_CSV = 'text/csv'


class SHCCustomerImportProcessor(DefaultCustomerImportProcessor):
    
    def __init__(self, user_subscription, size_limit_bytes=10 * 1024 * 1024, accept_types=[CONTENT_TYPE_XLSX, CONTENT_TYPE_CSV]) -> None:
        super().__init__(user_subscription, size_limit_bytes, accept_types)
        self.sheet_name = 'Organization'

    def save_data(self, data):
        point_expire_at = datetime.utcnow()+timedelta(days=30*6)
        for object in data:
            try:
                
                _, customer = lib.helper.login_helper.create_or_get_user(object.get('Email','').lower(), models.user.user.TYPE_BUYER,  user_name=object.get('Name'))
                
                #delete all point transactions if there are
                customer.point_transactions.all().delete()


                #create initial point transaction
                models.user.point_transaction.PointTransaction.objects.create(
                    buyer = customer,
                    user_subscription = self.user_subscription,
                    earned = object.get('PointsEarned'),
                    used = object.get('PointsUsed'),
                    expired_at = point_expire_at,
                    remark = "migrate from ordr_startr"
                )

                #create wallet
                if not models.user.buyer_wallet.BuyerWallet.objects.filter(user_subscription = self.user_subscription, buyer=customer).exists():
                    models.user.buyer_wallet.BuyerWallet.objects.create(
                    user_subscription = self.user_subscription,
                    buyer = customer,
                    points = max(object.get('PointsEarned') - object.get('PointsUsed'), 0)
                    )
                else:
                    wallet = models.user.buyer_wallet.BuyerWallet.objects.get(user_subscription = self.user_subscription, buyer=customer)
                    wallet.points = max(object.get('PointsEarned') - object.get('PointsUsed'), 0)
                    wallet.save()

                #add to user_subscription
                if not self.user_subscription.customers.filter(id=customer.id).exists():
                    self.user_subscription.customers.add(customer)

                # break
            except Exception:
                import traceback
                print(traceback.format_exc())


