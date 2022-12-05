import pytest

from django.urls import reverse
from django.test.client import MULTIPART_CONTENT, BOUNDARY
from api import models
import lib

import database
from datetime import datetime, timedelta
@pytest.mark.django_db(transaction=False)
def test_order_point_expired():

    startup_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'user_subscription':{'name':'test_user_subscription'},
        'user':{'email':'test@email.com'},
    })

    transaction_data_1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'point_transaction':{'buyer_id':startup_data.get('user_id'), 'earned':10, },
    }, **startup_data.copy())

    transaction_data_2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'point_transaction':{'buyer_id':startup_data.get('user_id'), 'earned':10, 'used':1, 'expired_at':datetime.utcnow()-timedelta(minutes=30)},
    }, **startup_data.copy())

    transaction_data_3 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'point_transaction':{'buyer_id':startup_data.get('user_id'), 'earned':10, 'used':1, 'expired_at':datetime.utcnow()-timedelta(minutes=10)},
    }, **startup_data.copy())

    transaction_data_4 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'point_transaction':{'buyer_id':startup_data.get('user_id'), 'earned':10, 'used':1},
    }, **startup_data.copy())

    wallet_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'buyer_wallet':{
            'buyer_id':startup_data.get('user_id'),
            'points':37
        },
    }, **startup_data.copy())

    end_at = datetime.utcnow()
    start_from = end_at - timedelta(days=1)

    lib.helper.wallet_helper.WalletHelper.adjust_all_wallet_with_expired_points(start_from=start_from, end_at=end_at)
    lib.helper.wallet_helper.WalletHelper.adjust_all_wallet_with_expired_points(start_from=start_from, end_at=end_at) 
    #event run this twice shouldn't effect the result

    wallet = models.user.buyer_wallet.BuyerWallet.objects.get(id = wallet_data.get('buyer_wallet_id'))

    assert wallet.points ==19


    #simulate expire points issued at long time ago
    point_transaction = models.user.point_transaction.PointTransaction.objects.get(id = transaction_data_1.get('point_transaction_id'))
    point_transaction.expired_at = datetime.utcnow()-timedelta(minutes=1)
    point_transaction.save()

    lib.helper.wallet_helper.WalletHelper.adjust_all_wallet_with_expired_points(start_from=start_from, end_at=end_at)
    lib.helper.wallet_helper.WalletHelper.adjust_all_wallet_with_expired_points(start_from=start_from, end_at=end_at) 
    #event run this twice shouldn't effect the result

    wallet = models.user.buyer_wallet.BuyerWallet.objects.get(id = wallet_data.get('buyer_wallet_id'))

    assert wallet.points ==10
    