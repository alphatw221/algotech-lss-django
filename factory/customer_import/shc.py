from .default import DefaultCustomerImportProcessor
import lib
from api import models
import math
from datetime import datetime, timedelta
class SHCCustomerImportProcessor(DefaultCustomerImportProcessor):
    
    def save_data(self, data):
        point_expire_at = datetime.utcnow()+timedelta(days=30*6)
        for object in data:
            try:
                
                _, customer = lib.helper.login_helper.create_or_get_user(object.get('Email'), models.user.user.TYPE_BUYER,  user_name=object.get('Name'))
                
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

            except Exception:
                import traceback
                print(traceback.format_exc())


