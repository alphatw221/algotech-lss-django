import pytest

from django.urls import reverse
from django.test.client import MULTIPART_CONTENT, BOUNDARY
from api import models
import lib

import database

@pytest.mark.django_db(transaction=False)
def test_overbook_equal_true():

    startup_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'user_subscription':{
            'name':'test_user_subscription'},
        'user':{'email':'test@email.com'},
        'campaign':{'title':'test'},
        'campaign_product':{
            'name':'test_campaign_product', 
            'order_code':'TEST', 
            'type':'product',
            'qty_for_sale':2, 
            'qty_add_to_cart':0, 
            'qty_sold':0, 
            'price':10,
            'overbook':True,
            'oversell':False
        }
    })

    cart_data_1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'cart':{
            'platform':'facebook',
            'customer_id':'1',
            'customer_name':'1',
            'customer_img':None,
        }
    }, **startup_data.copy())
    

    cart_data_2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'cart':{
            'platform':'facebook',
            'customer_id':'2',
            'customer_name':'2',
            'customer_img':None,
        }
    }, **startup_data.copy())

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    cart_1 = models.cart.cart.Cart.objects.get(id=cart_data_1.get('cart_id'))
    cart_2 = models.cart.cart.Cart.objects.get(id=cart_data_2.get('cart_id'))
    
    lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_1, campaign_product, 2)
    lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_2, campaign_product, 1)

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_add_to_cart == 3

    cart_2 = models.cart.cart.Cart.objects.get(id=cart_data_2.get('cart_id'))
    lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_2, campaign_product, 2)
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_add_to_cart == 4


@pytest.mark.django_db(transaction=False)
def test_overbook_equal_false():

    startup_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'user_subscription':{
            'name':'test_user_subscription'},
        'user':{'email':'test@email.com'},
        'campaign':{'title':'test'},
        'campaign_product':{
            'name':'test_campaign_product', 
            'order_code':'TEST', 
            'type':'product',
            'qty_for_sale':2, 
            'qty_add_to_cart':0, 
            'qty_sold':0, 
            'price':10,
            'overbook':False,
            'oversell':False
        }
    })

    cart_data_1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'cart':{
            'platform':'facebook',
            'customer_id':'1',
            'customer_name':'1',
            'customer_img':None,
        }
    }, **startup_data.copy())
    

    cart_data_2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'cart':{
            'platform':'facebook',
            'customer_id':'2',
            'customer_name':'2',
            'customer_img':None,
        }
    }, **startup_data.copy())

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    cart_1 = models.cart.cart.Cart.objects.get(id=cart_data_1.get('cart_id'))
    cart_2 = models.cart.cart.Cart.objects.get(id=cart_data_2.get('cart_id'))
    
    lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_1, campaign_product, 1)
    
    try:
        lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_2, campaign_product, 2)
    except Exception:
        pass
    
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_add_to_cart == 1

    cart_2 = models.cart.cart.Cart.objects.get(id=cart_data_2.get('cart_id'))
    lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_2, campaign_product, 1)
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_add_to_cart == 2

    cart_2 = models.cart.cart.Cart.objects.get(id=cart_data_2.get('cart_id'))
    try:
        lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_2, campaign_product, 2)
    except Exception:
        pass

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_add_to_cart == 2


@pytest.mark.django_db
def test_oversell_equal_true(client):

    startup_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'user_subscription':{
            'name':'test_user_subscription'},
        'user':{'email':'test@email.com'},
        'campaign':{'title':'test'},
        'campaign_product':{
            'name':'test_campaign_product', 
            'order_code':'TEST', 
            'type':'product',
            'qty_for_sale':2,               ##
            'qty_add_to_cart':0,            ##
            'qty_sold':0,                   ##
            'price':10,
            'overbook':False,               #overbook value should not matter if oversell == True
            'oversell':True
        }
    })

    cart_data_1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'cart':{
            'platform':'facebook',
            'customer_id':'1',
            'customer_name':'1',
            'customer_img':None,
        }
    }, **startup_data.copy())
    
    cart_data_2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'cart':{
            'platform':'facebook',
            'customer_id':'2',
            'customer_name':'2',
            'customer_img':None,
        }
    }, **startup_data.copy())

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    cart_1 = models.cart.cart.Cart.objects.get(id=cart_data_1.get('cart_id'))
    cart_2 = models.cart.cart.Cart.objects.get(id=cart_data_2.get('cart_id'))

    lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_1, campaign_product, 1)
    lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_2, campaign_product, 2)
    
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 0
    assert campaign_product.qty_add_to_cart ==3
    
    #checkout
    lib.helper.cart_helper.CartHelper.checkout(None, campaign_product.campaign, cart_1.id, None, {})
    lib.helper.cart_helper.CartHelper.checkout(None, campaign_product.campaign, cart_2.id, None, {})
    
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 3
    assert campaign_product.qty_add_to_cart ==0

    #payment
    pymongo_order1 = database.lss.order.Order.get_object(platform = cart_1.platform, customer_id=cart_1.customer_id, campaign_id = cart_1.campaign.id)
    pymongo_order2 = database.lss.order.Order.get_object(platform = cart_2.platform, customer_id=cart_2.customer_id, campaign_id = cart_2.campaign.id)

    url = reverse('order-buyer_upload_receipt', kwargs={'order_oid':str(pymongo_order1._id)} )
    response = client.put(url, content_type=MULTIPART_CONTENT, data={'last_five_digit':'12345', 'account_name':'test_account', 'account_mode':'test_mode'})
    assert response.status_code==200

    url = reverse('order-buyer_upload_receipt', kwargs={'order_oid':str(pymongo_order2._id)} )
    response = client.put(url, content_type=MULTIPART_CONTENT, data={'last_five_digit':'12345', 'account_name':'test_account', 'account_mode':'test_mode'})
    assert response.status_code==200

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 3
    assert campaign_product.qty_pending_payment == 0
    assert campaign_product.qty_add_to_cart ==0




@pytest.mark.django_db
def test_oversell_equal_false(client):


    startup_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'user_subscription':{
            'name':'test_user_subscription'},
        'user':{'email':'test@email.com'},
        'campaign':{'title':'test'},
        'campaign_product':{
            'name':'test_campaign_product', 
            'order_code':'TEST', 
            'type':'product',
            'qty_for_sale':2, 
            'qty_add_to_cart':0, 
            'qty_sold':0, 
            'price':10,
            'overbook':True,
            'oversell':False
        }
    })

    cart_data_1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'cart':{
            'platform':'facebook',
            'customer_id':'1',
            'customer_name':'1',
            'customer_img':None,
        }
    }, **startup_data.copy())
    

    cart_data_2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'cart':{
            'platform':'facebook',
            'customer_id':'2',
            'customer_name':'2',
            'customer_img':None,
        }
    }, **startup_data.copy())

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    cart_1 = models.cart.cart.Cart.objects.get(id=cart_data_1.get('cart_id'))
    cart_2 = models.cart.cart.Cart.objects.get(id=cart_data_2.get('cart_id'))
    
    lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_1, campaign_product, 1)
    lib.helper.cart_helper.CartHelper.update_cart_product(None, cart_2, campaign_product, 2)

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 0
    assert campaign_product.qty_add_to_cart ==3

    #checkout

    lib.helper.cart_helper.CartHelper.checkout(None, campaign_product.campaign, cart_1.id, None, {})
    try:
        lib.helper.cart_helper.CartHelper.checkout(None, campaign_product.campaign, cart_2.id, None, {})
    except Exception:
        pass
    
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 1
    assert campaign_product.qty_add_to_cart ==1

    lib.helper.cart_helper.CartHelper.checkout(None, campaign_product.campaign, cart_2.id, None, {})
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 2
    assert campaign_product.qty_add_to_cart == 0

    #payment

    pymongo_order1 = database.lss.order.Order.get_object(platform = cart_1.platform, customer_id=cart_1.customer_id, campaign_id = cart_1.campaign.id)
    pymongo_order2 = database.lss.order.Order.get_object(platform = cart_2.platform, customer_id=cart_2.customer_id, campaign_id = cart_2.campaign.id)

    url = reverse('order-buyer_upload_receipt', kwargs={'order_oid':str(pymongo_order1._id)} )
    response = client.put(url, content_type=MULTIPART_CONTENT, data={'last_five_digit':'12345', 'account_name':'test_account', 'account_mode':'test_mode'})
    assert response.status_code==200

    url = reverse('order-buyer_upload_receipt', kwargs={'order_oid':str(pymongo_order2._id)} )
    response = client.put(url, content_type=MULTIPART_CONTENT, data={'last_five_digit':'12345', 'account_name':'test_account', 'account_mode':'test_mode'})
    assert response.status_code==200

    # guest_upload_receipt
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 2
    assert campaign_product.qty_pending_payment == 0
    assert campaign_product.qty_add_to_cart == 0



