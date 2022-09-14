from api import models

def to_lss_product(ordr_startr_product, user_subscription):
    return {
        'name':ordr_startr_product.get('keyword'),
        'max_order_amount':ordr_startr_product.get('maxQty'),
        'sku':ordr_startr_product.get('SKU'),
        'order_code':ordr_startr_product.get('keyword'),
        'price':ordr_startr_product.get('price'),
        'qty':int(ordr_startr_product.get('stock'))-int(ordr_startr_product.get('sold')),
        'tag':[ordr_startr_product.get('supplierName')],
        'description':ordr_startr_product.get('description'),
        'user_subscription':user_subscription,
        'status':models.product.product.STATUS_DISABLED if ordr_startr_product.get('visible')==False else models.product.product.STATUS_ENABLED
        

    }

def to_lss_order(ordr_startr_order_data, pre_order, campaign_product_external_internal_map):



    lss_products = {}
    subtotal = 0
    for item in ordr_startr_order_data.get('Items',[]):
        subtotal+=item.get('total',0)
        if item.get('id') not in campaign_product_external_internal_map:
            continue
        lss_campaign_product_data = campaign_product_external_internal_map[item.get('id')]
        lss_products[str(lss_campaign_product_data.get('id'))] = {
            "order_product_id":None,   #TODO
            "name":lss_campaign_product_data.get('name'),
            "image":lss_campaign_product_data.get('image'),
            "price":float(item.get('price')),
            "type":lss_campaign_product_data.get('type'),
            "qty":float(item.get('qty')),
            "subtotal":float(item.get('total'))
        }


    return {
        "campaign":pre_order.campaign,
        "customer_id":pre_order.customer_id,
        "customer_name":pre_order.customer_name,
        "customer_img":pre_order.customer_img,
        "platform":pre_order.platform,
        "platform_id":pre_order.platform_id,
        "subtotal":subtotal,
        "total":ordr_startr_order_data.get('Total',0),

        "shipping_cost":ordr_startr_order_data.get('ShippingCharge',0),

        "shipping_first_name":ordr_startr_order_data.get('ShippingName'),
        "shipping_last_name":"",
        "shipping_email":ordr_startr_order_data.get('ShippingEmail'),
        "shipping_phone":ordr_startr_order_data.get('ShippingMobile'),
        "shipping_postcode":ordr_startr_order_data.get('ShippingPostalCode'),
        "shipping_address_1":ordr_startr_order_data.get('ShippingAddress1'),

        "status":models.order.order.STATUS_COMPLETE if ordr_startr_order_data.get('PaymentStatus')=='paid' else models.order.order.STATUS_REVIEW,
        "meta":{
            'ordr_startr':{
                'id':ordr_startr_order_data.get('_id')
            }
        },

        "products":lss_products
    }

# def to_lss_order(ordr_startr_order_data, lss_pre_order_data):



#     subtotal = 0
#     for item in ordr_startr_order_data.get('Items',[]):
#         subtotal+=item.get('total',0)


#     return {
#         "campaign_id":lss_pre_order_data.get('campaign_id'),
#         "customer_id":lss_pre_order_data.get('customer_id'),
#         "customer_name":lss_pre_order_data.get('customer_name'),
#         "customer_img":lss_pre_order_data.get('customer_img'),
#         "platform":lss_pre_order_data.get('platform'),
#         "platform_id":lss_pre_order_data.get('platform_id'),
#         "subtotal":subtotal,
#         "total":ordr_startr_order_data.get('Total',0),

#         "shipping_cost":ordr_startr_order_data.get('ShippingCharge',0),

#         "shipping_first_name":ordr_startr_order_data.get('ShippingName'),
#         "shipping_last_name":"",
#         "shipping_email":ordr_startr_order_data.get('ShippingEmail'),
#         "shipping_phone":ordr_startr_order_data.get('ShippingMobile'),
#         "shipping_postcode":ordr_startr_order_data.get('ShippingPostalCode'),
#         "shipping_address_1":ordr_startr_order_data.get('ShippingAddress1'),
#         "shipping_address_2":ordr_startr_order_data.get('ShippingAddress2'),
#         "status":models.order.order.STATUS_COMPLETE if ordr_startr_order_data.get('PaymentStatus')=='paid' else models.order.order.STATUS_REVIEW,
#         "meta":{
#             'ordr_startr':{
#                 'id':ordr_startr_order_data.get('_id')
#             }
#         }
#     }


    # {
    #     "order":{
    #         "FbId":"4422762234485468",
    #         "Status":"confirmed",
    #         "Is_FirstOrder":false,
    #         "ShippingCharge":0,
    #         "PaymentStatus":"paid",
    #         "DiscountAmount":0,
    #         "PaidAmount":270,
    #         "Payment_id":"payment_9a4d7cc159c13798c4fbe94199ae5d06",
    #         "ApplyPoint":0,
    #         "DiscountAmountPoint":0,
    #         "OrderWisePoint":540,
    #         "PaymentClientStatus":"completed",
    #         "DeductQtyUponPaymentStatus":"",
    #         "ReferralCode":"",
    #         "OrcCode":"",
    #         "HideDeliveryMessage":"Supplier will contact you within 5 working days to arrange delivery with you. 🙂",
    #         "RemarkMessage":"Remark Message",
    #         "FeedBackMessage":"hello Feedback",
    #         "_id":"6315c4d91cd21f3691d51b80",
    #         "FbPageId":"105929794479727",
    #         "sourceType":"FB",
    #         "Date":"2022-09-06T06:10:48.000Z",
    #         "DeliveryTimeSlot":null,
    #         "Items":[
    #             {"_id":"6316e468513eb16642f00c54","id":"6315cc771cd21f3691d51ba7","itemName":"Caribbean S.Bag (WxHxD: 13.5\"x8.7\"x5.5\")","qty":1,"price":270,"keyword":"CB01","SKU":"CB01","total":270,"supplierName":"Korea","Date":"2022-09-06T06:10:48.000Z"}
    #             ],
    #         "Name":"Yi-Hsueh Lin",
    #         "Residential_Type":"HDB",
    #         "ShippingAddress1":"abc",
    #         "ShippingEmail":"abc@gmail.com",
    #         "ShippingMobile":"8401060120",
    #         "ShippingName":"Yi-Hsueh Lin",
    #         "ShippingPostalCode":"123456",
    #         "ShippingSupplier":[],
    #         "Total":270,
    #         "__v":0,
    #         "createdAt":"2022-09-05T09:43:53.161Z",
    #         "updatedAt":"2022-09-06T17:45:27.686Z",
    #         "MisMatchItems":[],
    #         "ValidItems":[],
    #         "ShippingAddress2":null,
    #         "PaymentDate":"2022-09-06T17:45:27.000Z"
    #     }
    # }