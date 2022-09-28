import pytest

from django.urls import reverse
from django.test.client import MULTIPART_CONTENT, BOUNDARY
from api import models
import lib

import database

# @pytest.mark.django_db(transaction=False)
# def test_overbook_equal_true():


#     startup_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
#         'user_subscription':{
#             'name':'test_user_subscription'},
#         'user':{'email':'test@email.com'},
#         'campaign':{'title':'test'},
#         'campaign_product':{
#             'name':'test_campaign_product', 
#             'order_code':'TEST', 
#             'type':'product',
#             'qty_for_sale':2, 
#             'qty_add_to_cart':0, 
#             'qty_sold':0, 
#             'price':10,
#             'overbook':True,
#             'oversell':True
#         }
#     })

#     pre_order_data1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
#         'pre_order':{
#             'platform':'facebook',
#             'customer_id':'1',
#             'customer_name':'1',
#             'customer_img':None,
#         }
#     }, **startup_data.copy())
    

#     pre_order_data2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
#         'pre_order':{
#             'platform':'facebook',
#             'customer_id':'2',
#             'customer_name':'2',
#             'customer_img':None,
#         }
#     }, **startup_data.copy())

#     campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
#     pre_order_1 = models.order.pre_order.PreOrder.objects.get(id=pre_order_data1.get('pre_order_id'))
#     pre_order_2 = models.order.pre_order.PreOrder.objects.get(id=pre_order_data2.get('pre_order_id'))

#     lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_1.id, campaign_product.id, 2)
#     lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_2.id, campaign_product.id, 1)

#     campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
#     assert campaign_product.qty_add_to_cart == 3

#     order_product = pre_order_2.order_products.first()
#     lib.helper.order_helper.PreOrderHelper.update_product(None, pre_order_2.id, order_product.id, 2)

#     campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
#     assert campaign_product.qty_add_to_cart == 4


# @pytest.mark.django_db(transaction=False)
# def test_overbook_equal_false():


#     startup_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
#         'user_subscription':{
#             'name':'test_user_subscription'},
#         'user':{'email':'test@email.com'},
#         'campaign':{'title':'test'},
#         'campaign_product':{
#             'name':'test_campaign_product', 
#             'order_code':'TEST', 
#             'type':'product',
#             'qty_for_sale':2, 
#             'qty_add_to_cart':0, 
#             'qty_sold':0, 
#             'price':10,
#             'overbook':False,
#             'oversell':True
#         }
#     })

#     pre_order_data1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
#         'pre_order':{
#             'platform':'facebook',
#             'customer_id':'1',
#             'customer_name':'1',
#             'customer_img':None,
#         }
#     }, **startup_data.copy())
    

#     pre_order_data2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
#         'pre_order':{
#             'platform':'facebook',
#             'customer_id':'2',
#             'customer_name':'2',
#             'customer_img':None,
#         }
#     }, **startup_data.copy())

#     campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
#     pre_order_1 = models.order.pre_order.PreOrder.objects.get(id=pre_order_data1.get('pre_order_id'))
#     pre_order_2 = models.order.pre_order.PreOrder.objects.get(id=pre_order_data2.get('pre_order_id'))

#     lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_1.id, campaign_product.id, 1)
#     try:
#         lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_2.id, campaign_product.id, 2)
#     except Exception:
#         pass

    
#     campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
#     assert campaign_product.qty_add_to_cart == 1


#     lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_2.id, campaign_product.id, 1)
#     campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
#     assert campaign_product.qty_add_to_cart == 2


#     order_product = pre_order_2.order_products.first()
#     try:
#         lib.helper.order_helper.PreOrderHelper.update_product(None, pre_order_2.id, order_product.id, 2)
#     except Exception:
#         pass

#     campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
#     assert campaign_product.qty_add_to_cart == 2







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

    pre_order_data1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'pre_order':{
            'platform':'facebook',
            'customer_id':'1',
            'customer_name':'1',
            'customer_img':None,
        }
    }, **startup_data.copy())
    

    pre_order_data2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'pre_order':{
            'platform':'facebook',
            'customer_id':'2',
            'customer_name':'2',
            'customer_img':None,
        }
    }, **startup_data.copy())

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    pre_order_1 = models.order.pre_order.PreOrder.objects.get(id=pre_order_data1.get('pre_order_id'))
    pre_order_2 = models.order.pre_order.PreOrder.objects.get(id=pre_order_data2.get('pre_order_id'))


    
    lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_1.id, campaign_product.id, 1)
    lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_2.id, campaign_product.id, 2)
    
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 0
    assert campaign_product.qty_add_to_cart ==3

    
    #checkout
    lib.helper.order_helper.PreOrderHelper.checkout(None, startup_data.get('campaign_id'), pre_order_1.id)
    lib.helper.order_helper.PreOrderHelper.checkout(None, startup_data.get('campaign_id'), pre_order_2.id)
    
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 3
    assert campaign_product.qty_add_to_cart ==0


    #payment
    pymongo_order1 = database.lss.order.Order.get_object(platform = pre_order_1.platform, customer_id=pre_order_1.customer_id, campaign_id = pre_order_1.campaign.id)
    pymongo_order2 = database.lss.order.Order.get_object(platform = pre_order_2.platform, customer_id=pre_order_2.customer_id, campaign_id = pre_order_2.campaign.id)


    url = reverse('order-guest_upload_receipt', kwargs={'order_oid':str(pymongo_order1._id)} )
    response = client.put(url, content_type=MULTIPART_CONTENT, data={'last_five_digit':'12345', 'account_name':'test_account', 'account_mode':'test_mode'})
    assert response.status_code==200

    url = reverse('order-guest_upload_receipt', kwargs={'order_oid':str(pymongo_order2._id)} )
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

    pre_order_data1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'pre_order':{
            'platform':'facebook',
            'customer_id':'1',
            'customer_name':'1',
            'customer_img':None,
        }
    }, **startup_data.copy())
    

    pre_order_data2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'pre_order':{
            'platform':'facebook',
            'customer_id':'2',
            'customer_name':'2',
            'customer_img':None,
        }
    }, **startup_data.copy())

    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    pre_order_1 = models.order.pre_order.PreOrder.objects.get(id=pre_order_data1.get('pre_order_id'))
    pre_order_2 = models.order.pre_order.PreOrder.objects.get(id=pre_order_data2.get('pre_order_id'))


    
    lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_1.id, campaign_product.id, 1)
    lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_2.id, campaign_product.id, 2)


    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 0
    assert campaign_product.qty_add_to_cart ==3

    #checkout

    lib.helper.order_helper.PreOrderHelper.checkout(None, startup_data.get('campaign_id'), pre_order_1.id)
    try:
        lib.helper.order_helper.PreOrderHelper.checkout(None, startup_data.get('campaign_id'), pre_order_2.id)
    except Exception:
        pass
    
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 1
    assert campaign_product.qty_add_to_cart ==1


    lib.helper.order_helper.PreOrderHelper.checkout(None, startup_data.get('campaign_id'), pre_order_2.id)
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_pending_payment == 2
    assert campaign_product.qty_add_to_cart == 0

    #payment

    pymongo_order1 = database.lss.order.Order.get_object(platform = pre_order_1.platform, customer_id=pre_order_1.customer_id, campaign_id = pre_order_1.campaign.id)
    
    pymongo_order2 = database.lss.order.Order.get_object(platform = pre_order_2.platform, customer_id=pre_order_2.customer_id, campaign_id = pre_order_2.campaign.id)



    url = reverse('order-guest_upload_receipt', kwargs={'order_oid':str(pymongo_order1._id)} )
    response = client.put(url, content_type=MULTIPART_CONTENT, data={'last_five_digit':'12345', 'account_name':'test_account', 'account_mode':'test_mode'})
    assert response.status_code==200

    url = reverse('order-guest_upload_receipt', kwargs={'order_oid':str(pymongo_order2._id)} )
    response = client.put(url, content_type=MULTIPART_CONTENT, data={'last_five_digit':'12345', 'account_name':'test_account', 'account_mode':'test_mode'})
    assert response.status_code==200


    # guest_upload_receipt
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=startup_data.get('campaign_product_id'))
    assert campaign_product.qty_for_sale == 2
    assert campaign_product.qty_sold == 2
    assert campaign_product.qty_pending_payment == 0
    assert campaign_product.qty_add_to_cart == 0



