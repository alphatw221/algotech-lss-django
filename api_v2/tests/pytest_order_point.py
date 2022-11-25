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

    order_data1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'order':{'buyer_id':startup_data.get('user_id'), 'points_earned':10, },
    }, **startup_data.copy())

    order_data2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'order':{'buyer_id':startup_data.get('user_id'), 'points_earned':10, 'points_used':1, 'point_expired_at':datetime.utcnow()-timedelta(minutes=30)},
    }, **startup_data.copy())

    order_data3 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'order':{'buyer_id':startup_data.get('user_id'), 'points_earned':10, 'points_used':1, 'point_expired_at':datetime.utcnow()-timedelta(minutes=10)},
    }, **startup_data.copy())

    order_data4 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'order':{'buyer_id':startup_data.get('user_id'), 'points_earned':10, 'points_used':1},
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
    order = models.order.order.Order.objects.get(id = order_data1.get('order_id'))
    order.point_expired_at = datetime.utcnow()-timedelta(minutes=1)
    order.save()

    lib.helper.wallet_helper.WalletHelper.adjust_all_wallet_with_expired_points(start_from=start_from, end_at=end_at)
    lib.helper.wallet_helper.WalletHelper.adjust_all_wallet_with_expired_points(start_from=start_from, end_at=end_at) 
    #event run this twice shouldn't effect the result

    wallet = models.user.buyer_wallet.BuyerWallet.objects.get(id = wallet_data.get('buyer_wallet_id'))

    assert wallet.points ==10
    