from .default import DefaultCustomerImportProcessor
import lib
from api import models
import math
from datetime import datetime, timedelta
class SHCCustomerImportProcessor(DefaultCustomerImportProcessor):
    
    def save_data(self, data):

        for object in data:
            try:
                
                auth_user, api_user = lib.helper.login_helper.create_or_get_user(object.get('Email'), models.user.user.TYPE_BUYER,  user_name=object.get('Name'))
                

                #create wallet
                if not models.user.buyer_wallet.BuyerWallet.objects.filter(user_subscription = self.user_subscription, buyer=api_user).exists():
                    models.user.buyer_wallet.BuyerWallet.objects.create(
                    user_subscription = self.user_subscription,
                    buyer = api_user,
                    points = max(object.get('PointsEarned') - object.get('PointsUsed'), 0)
                    )
                else:
                    wallet = models.user.buyer_wallet.BuyerWallet.objects.get(user_subscription = self.user_subscription, buyer=api_user)
                    wallet.points = max(object.get('PointsEarned') - object.get('PointsUsed'), 0)
                    wallet.save()

                #delete all point transactions if there are

                #create initial point transaction


                #add to user_subscription
                if not self.user_subscription.customers.filter(id=api_user.id).exists():
                    self.user_subscription.customers.add(api_user)

            except Exception:
                import traceback
                print(traceback.format_exc())


