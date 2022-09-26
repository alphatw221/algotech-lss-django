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


@pytest.mark.django_db
def test_create_data_helper():
    data = lib.helper.unit_test_helper.UnitTestHelper.create_test_data(collections_data={
        'user_subscription':{'name':'test_user_subscription'},
        'campaign':{'title':'test'}
    })

    print(data)


# def test_payment_callback(client):
    

#     url = reverse('ordr_startr:order-payment_complete_callback', kwargs={'user_subscription_id':1}) #'<namespace>:<view_set_name>-<url_name>'
#     headers = {'Authorization':'Token eyJhbGciOiAic2hhMjU2IiwgInR5cCI6ICJ2MSJ9.eyJrZXkiOiAiN2JiZHJBNWtRMDZuQVpQOWllRWhUQSIsICJwZXJtIjoge30sICJhdXRoIjogbnVsbCwgIm1ldGEiOiB7fSwgImV4cCI6IDE2NjI1NDAyNjh9.8a1a3f2735e90bd3a8abd9615e7bc26e5860297968250268d371a31728c04556.7bbdrA5kQ06nAZP9ieEhTA.a1ttdUyxI3KdlcO1evA_Fyy1icAxQd8nXgGUlEThLoE'}
#     data = {
#         "order":{
#             "FbId":"5134093353312051",
#             "Status":"confirmed",
#             "Is_FirstOrder":True,
#             "ShippingCharge":0,
#             "PaymentStatus":"paid",
#             "DiscountAmount":0,
#             "PaidAmount":1150,
#             "Payment_id":"payment_8550798dce33aacdb5ac6c7752e52b78",
#             "ApplyPoint":0,
#             "DiscountAmountPoint":0,
#             "OrderWisePoint":2300,
#             "PaymentClientStatus":"completed",
#             "DeductQtyUponPaymentStatus":"",
#             "ReferralCode":"",
#             "OrcCode":"",
#             "HideDeliveryMessage":"Supplier will contact you within 5 working days to arrange delivery with you. �",
#             "RemarkMessage":"Remark Message",
#             "FeedBackMessage":"",
#             "ExternalReferenceId":"63197fd40b497c2c440f71a1",
#             "id":"63198013608d6432adc048a7",
#             "FbPageId":"105929794479727",
#             "sourceType":"FB",
#             "Date":"2022-09-08T05:39:31.000Z",
#             "DeliveryTimeSlot":None,
#             "Items":[{"_id":"63198013608d6432adc048a8","id":"6315cc771cd21f3691d51bab","itemName":"Naomi Card Wallet -Black (WxH: 4.4\"x3.2\")","qty":3,"price":230,"keyword":"NW01","SKU":"NW01","total":690,"supplierName":"Korea","Date":"2022-09-08T05:39:31.000Z"},{"_id":"63198013608d6432adc048a9","id":"6315cc771cd21f3691d51bac","itemName":"Naomi Card Wallet -Butter (WxH: 4.4\"x3.2\")","qty":2,"price":230,"keyword":"NW02","SKU":"NW02","total":460,"supplierName":"Korea","Date":"2022-09-08T05:39:31.000Z"}],
#             "Name":"鄭曉筠",
#             "Residential_Type":"Landed",
#             "ShippingAddress1":"Tpe",
#             "ShippingEmail":"ceciliacheng@accoladeglobal.net",
#             "ShippingMobile":"0938865798",
#             "ShippingName":"鄭曉筠",
#             "ShippingPostalCode":"333",
#             "ShippingSupplier":[],
#             "Total":1150,
#             "v":0,
#             "createdAt":"2022-09-08T05:39:31.134Z",
#             "updatedAt":"2022-09-08T05:59:07.565Z",
#             "MisMatchItems":[],
#             "ValidItems":[],
#             "ShippingAddress2":None,
#             "PaymentDate":"2022-09-08T05:59:07.000Z"},

#             "products":[
#                 {"maxQty":5,"defaultMaxQty":5,"SKU":"NW01","visible":True,"sold":3,"supplierName":"Korea","counter":29,"_id":"6315cc771cd21f3691d51bab","description":"Naomi Card Wallet -Black (WxH: 4.4\"x3.2\")","keyword":"NW01","price":230,"stock":2,"reply_message":"Naomi Card Wallet -Black (WxH: 4.4\"x3.2\")","FbPageId":"105929794479727","createdAt":"2022-09-05T10:16:23.972Z","updatedAt":"2022-09-08T05:57:18.132Z","v":0},{"maxQty":5,"defaultMaxQty":5,"SKU":"NW02","visible":true,"sold":2,"supplierName":"Korea","counter":30,"_id":"6315cc771cd21f3691d51bac","description":"Naomi Card Wallet -Butter (WxH: 4.4\"x3.2\")","keyword":"NW02","price":230,"stock":3,"reply_message":"Naomi Card Wallet -Butter (WxH: 4.4\"x3.2\")","FbPageId":"105929794479727","createdAt":"2022-09-05T10:16:24.002Z","updatedAt":"2022-09-08T05:57:18.136Z","_v":0}
#                 ]
#             }
#     response = client.put(url,headers={'Authorization':'Token 123asd'},json={})

#     assert response.status_code==200

    # assert campaign_product qty correct







