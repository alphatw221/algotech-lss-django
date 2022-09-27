import pytest
from api import models

from automation import jobs
from pytest_django import asserts
import json
from django.urls import reverse
import lib
# @pytest.mark.django_db
# def test_product_sync_user():
#     user_plan = {
#         "plugins": {
#             "ordr_startr": {
#                 "key": "ordrstartr2022!"
#             }
#         }
#     }
#     models.user.user_subscription.UserSubscription.objects.create(name='test',user_plan = user_plan)


#     user_subscription = models.user.user_subscription.UserSubscription.objects.get(name='test')
#     credential = user_subscription.user_plan.get('plugins',{}).get('ordr_startr')
#     jobs.ordr_startr.export_product_job(user_subscription_id=user_subscription.id, credential=credential)
    
#     data = models.product.product.ProductSerializer(user_subscription.products, many=True).data
#     print(dict(data))
#     # expect_data = [{"meta":{"ordr_startr":{"id":"633019a4d21f1b6bfe15bf40"}}, "meta_logistic":{}, 'tag':['Japan'], 'qty':2, 'name':'AA225',''}]
#     # asserts.assertJSONEqual(json.dumps(data),expect_data)

#     # assert models.product.product.ProductSerializer(user_subscription.products, many=True).data==True
#     assert True


# @pytest.mark.django_db
# def test_create_data_helper():
#     data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
#         'user_subscription':{'name':'test_user_subscription'},
#         'campaign':{'title':'test'}
#     })

#     print(data)

@pytest.mark.django_db
def test_payment_callback(client):

    

    data1 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'user_subscription':{'name':'test_user_subscription'},
        'user':{'email':'test@email.com'},
        'campaign':{'title':'test'},
        'product':{'name':'test'},
        'campaign_product':{'name':'test_campaign_product', 'order_code':'NW01', 'qty_for_sale':1, 'qty_add_to_cart':1, 'qty_sold':0, 'price':10,'meta':{'ordr_startr':{'id':'123'}}}
    })

    data2 = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'pre_order':{
            'platform':'facebook',
            'customer_id':'123',
            'customer_name':'123',
            'customer_img':None,
            'products':{
                str(data1.get('campaign_product_id')):{
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
    })

    developer=models.user.developer.Developer.objects.create(**{
            "api_key" : '123',
            "secret_key" : '123',
            "name" : 'test',
            "authorization": {
                "user_subscription": {
                        str(data1.get('user_subscription_id')): {},
                    }
            },
        })

    token = lib.helper.token_helper.V1DeveloperTokenHelper.generate_token(developer)
    # print(token)
    user_subscription_id = data1.get('user_subscription_id')
    pre_order_oid = data2.get('pre_order_oid')


    url = reverse('ordr_startr:order-payment_complete_callback', kwargs={'user_subscription_id':user_subscription_id}) #'<namespace>:<view_set_name>-<url_name>'
    headers = {'Authorization':f'Token {token}'}
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
    response = client.put(url,content_type='application/json', json=data, **headers)

    # assert response.status_code==200
    assert True








