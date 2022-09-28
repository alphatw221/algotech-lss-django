import pytest
from api import models

from automation import jobs
from pytest_django import asserts
import json
from django.urls import reverse
import lib


def __get_startup_data():
    startup_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'user_subscription':{
            'name':'test_user_subscription', 
            'user_plan':{
                "plugins": {
                    "ordr_startr": {
                        "key": "ordrstartr2022!"
                    }
                }
            }},
        'user':{'email':'test@email.com'},
        'campaign':{'title':'test'},
        # 'product':{'name':'test'},
        'campaign_product':{
            'name':'test_campaign_product', 
            'order_code':'NW01', 
            'type':'product',
            'qty_for_sale':1, 
            'qty_add_to_cart':1, 
            'qty_sold':0, 
            'price':10,
            'meta':{'ordr_startr':{'id':'123'}}}
    })

    startup_data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'pre_order':{
            'platform':'facebook',
            'customer_id':'123',
            'customer_name':'123',
            'customer_img':None,
            'products':{
                str(startup_data.get('campaign_product_id')):{
                    "order_product_id": None,
                    "name": "test_campaign_product",
                    "image": None,
                    "price": 10,
                    "type": "product",
                    "qty": 1,
                    "subtotal": 10
                }
            }   
        }
    }, **startup_data)

    return startup_data



@pytest.mark.django_db(transaction=False)
def test_product_sync(client):
    startup_data = __get_startup_data()
    user_subscription = models.user.user_subscription.UserSubscription.objects.get(id=startup_data.get('user_subscription_id'))
    credential = user_subscription.user_plan.get('plugins',{}).get('ordr_startr')

    jobs.ordr_startr.export_product_job(user_subscription_id=user_subscription.id, credential=credential)
    

    the_only_product = user_subscription.products.all().first()


    assert the_only_product.meta == {
            'ordr_startr':{
                'id':'123'
            }
        }
    assert the_only_product.tag == ['Japan']
    assert the_only_product.qty==1
    assert the_only_product.name=='test'
    assert the_only_product.price==10.0
    assert the_only_product.type =='product'
    



@pytest.mark.django_db(transaction=False)
def test_payment_callback(client):
    startup_data = __get_startup_data()

    developer=models.user.developer.Developer.objects.create(**{
            "api_key" : '123',
            "secret_key" : '123',
            "name" : 'test',
            "authorization": {
                "user_subscription": {
                        str(startup_data.get('user_subscription_id')): {},
                    }
            },
        })

    token = lib.helper.token_helper.V1DeveloperTokenHelper.generate_token(developer)

    user_subscription_id = startup_data.get('user_subscription_id')
    pre_order_oid = startup_data.get('pre_order_oid')


    url = reverse('ordr_startr:order-payment_complete_callback', kwargs={'user_subscription_id':user_subscription_id}) #'<namespace>:<view_set_name>-<url_name>'

    headers = {
        'HTTP_X_HTTP_METHOD_OVERRIDE': 'PUT',
        'HTTP_AUTHORIZATION':f'Token {token}'
        }

    data = {
        "order":{
            "FbId":"5134093353312051",
            "Status":"confirmed",
            "Is_FirstOrder":True,
            "ShippingCharge":0,
            "PaymentStatus":"paid",
            "DiscountAmount":0,
            "PaidAmount":10,
            "Payment_id":"payment_8550798dce33aacdb5ac6c7752e52b78",
            "ApplyPoint":0,
            "DiscountAmountPoint":0,
            "OrderWisePoint":2300,
            "PaymentClientStatus":"completed",
            "DeductQtyUponPaymentStatus":"",
            "ReferralCode":"",
            "OrcCode":"",
            "HideDeliveryMessage":"Supplier will contact you within 5 working days to arrange delivery with you. �",
            "RemarkMessage":"Remark Message",
            "FeedBackMessage":"",
            "ExternalReferenceId":pre_order_oid,
            "id":"63198013608d6432adc048a7",
            "FbPageId":"105929794479727",
            "sourceType":"FB",
            "Date":"2022-09-08T05:39:31.000Z",
            "DeliveryTimeSlot":None,

            "Items":[
                {"_id":"123",               #*
                "id":"123",                 #*
                "itemName":"Naomi Card Wallet -Black (WxH: 4.4\"x3.2\")",
                "qty":1,                    #*
                "price":10,                 #*
                "keyword":"NW01",
                "SKU":"NW01",
                "total":10  ,                #*
                "supplierName":"Korea",
                "Date":"2022-09-08T05:39:31.000Z"}],

            "Name":"鄭曉筠",
            "Residential_Type":"Landed",
            "ShippingAddress1":"Tpe",
            "ShippingEmail":"ceciliacheng@accoladeglobal.net",
            "ShippingMobile":"0938865798",
            "ShippingName":"鄭曉筠",
            "ShippingPostalCode":"333",
            "ShippingSupplier":[],
            "Total":10,
            "v":0,
            "createdAt":"2022-09-08T05:39:31.134Z",
            "updatedAt":"2022-09-08T05:59:07.565Z",
            "MisMatchItems":[],
            "ValidItems":[],
            "ShippingAddress2":None,
            "PaymentDate":"2022-09-08T05:59:07.000Z"},

            "products":[
                {
                    "maxQty":5,
                    "defaultMaxQty":5,
                    "SKU":"NW01",
                    "visible":True,
                    "sold":1,                       #*
                    "supplierName":"Korea",
                    "counter":29,
                    "_id":"123",
                    "description":"Naomi Card Wallet -Black (WxH: 4.4\"x3.2\")","keyword":"NW01",
                    "price":10,                     #*
                    "stock":0,                      #*
                    "reply_message":"Naomi Card Wallet -Black (WxH: 4.4\"x3.2\")","FbPageId":"105929794479727","createdAt":"2022-09-05T10:16:23.972Z","updatedAt":"2022-09-08T05:57:18.132Z","v":0}
                ]
            }

    


    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id = startup_data.get('campaign_product_id'))
    assert campaign_product.qty_sold == 0
    assert campaign_product.qty_add_to_cart == 1

    pre_order = models.order.pre_order.PreOrder.objects.get(id=startup_data.get('pre_order_id'))
    assert str(campaign_product.id) in pre_order.products

    response = client.put(url,content_type='application/json', data=data, **headers)

    assert response.status_code==200

    #check pre_order has been cleared
    pre_order = models.order.pre_order.PreOrder.objects.get(id=startup_data.get('pre_order_id'))
    assert pre_order.products=={}


    #check campaign product qty
    campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id = startup_data.get('campaign_product_id'))
    assert campaign_product.qty_sold == 1
    assert campaign_product.qty_add_to_cart == 0

    
    #check order has been created
    order = models.order.order.Order.objects.filter(platform = pre_order.platform, customer_id = pre_order.customer_id, campaign = pre_order.campaign).first()
    assert order != None
    assert order.total == 10
    assert str(campaign_product.id) in order.products

    






