from django.http import JsonResponse
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from api import models
from api import rule

from automation import jobs

import lib
import datetime
import uuid
import service
import database
import traceback

class CartPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CartViewSet(viewsets.ModelViewSet):
    queryset = models.cart.cart.Cart.objects.all().order_by('id')
    serializer_class = models.cart.cart.CartSerializer
    filterset_fields = []
    pagination_class = CartPagination

# ---------------------------------------------- guest ------------------------------------------------------
    @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<cart_oid>[^/.]+)/platform', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_retrieve_cart_platform(self, request, cart_oid):
        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        return Response(cart.platform, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<cart_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_retrieve_cart(self, request, cart_oid):
        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_oid>[^/.]+)/guest/edit', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.cart_operation_error_handler.order_operation_error_handler
    def guest_edit_cart_product(self, request, cart_oid):

        campaign_product_id, qty = lib.util.getter.getdata(request, ('campaign_product_id', 'qty',), required=True)

        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
        campaign_product = campaign.products.get(id=campaign_product_id) if campaign.products.filter(id=campaign_product_id).exists() else None

        ret = rule.rule_checker.cart_rule_checker.CartEditProductRuleChecker.check(
            **{'cart':cart,'campaign':campaign, 'campaign_product_id':campaign_product_id, 'api_user':None, 'qty':qty})
        qty_difference = ret.get('qty_difference')

        database.lss.campaign_product.CampaignProduct(id=campaign_product.id).add_to_cart(qty_difference, sync=False)

        cart.products[campaign_product_id]={'qty':qty}
        cart.save()

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['DELETE'], url_path=r'(?P<cart_oid>[^/.]+)/guest/delete', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.cart_operation_error_handler.order_operation_error_handler
    def guest_delete_cart_product(self, request, cart_oid):

        campaign_product_id, = lib.util.getter.getdata(request, ('campaign_product_id', ), required=True)

        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
        campaign_product = campaign.products.get(id=campaign_product_id) if campaign.products.filter(id=campaign_product_id).exists() else None


        rule.rule_checker.cart_rule_checker.CartDeleteProductRuleChecker.check({'api_user':None,'cart':cart,'campaign_product':campaign_product})

        if campaign_product_id not in cart.products:
            raise lib.error_handle.error.api_error.ApiVerifyError('campaign_product not found')
        
        qty = cart.products[campaign_product_id].get('qty',0)
        database.lss.campaign_product.CampaignProduct(id=campaign_product_id).customer_return(qty=qty, sync=False)

        del cart.products[campaign_product_id]
        cart.save()

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_oid>[^/.]+)/guest/checkout', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.cart_operation_error_handler.order_operation_error_handler
    def guest_checkout_cart(self, request, cart_oid):
        
        shipping_data, = \
            lib.util.getter.getdata(request, ("shipping_data",), required=True)

        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)

        rule.rule_checker.cart_rule_checker.CartCheckoutRuleChecker.check({'api_user':None, 'campaign':campaign, 'cart':cart})

        serializer = models.order.order.OrderSerializerUpdateShipping(data=shipping_data) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #checkout
        success, api_order = lib.helper.cart_helper.CartHelper.checkout(None, campaign.id, cart.id)


        if not success:
            cart = lib.util.verify.Verify.get_cart(cart.id)
            return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_205_RESET_CONTENT)

        order = lib.util.verify.Verify.get_order(api_order.id)

        serializer = models.order.order.OrderSerializerUpdateShipping(order, data=shipping_data, partial=True) 
        if not serializer.is_valid():
            data = models.order.order.OrderSerializer(order).data
            data['oid']=str(api_order._id)
            return Response(data, status=status.HTTP_200_OK)

        order = serializer.save()

        content = lib.helper.order_helper.OrderHelper.get_checkout_email_content(order,api_order._id)
        jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)     #queue this to redis if needed
        
        data = models.order.order.OrderSerializer(order).data
        data['oid']=str(api_order._id)

        #send email to customer over here order detail link
        return Response(data, status=status.HTTP_200_OK)




    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/guest/create', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_create_cart(self, request, campaign_id):

        recaptcha_token, client_uuid = lib.util.getter.getparams(request, ('recaptcha_token', 'client_uuid'), with_user=False)
        
        code, response = service.recaptcha.recaptcha.verify_token(recaptcha_token)

        if code!=200 or not response.get('success'):
            raise lib.error_handle.error.api_error.ApiVerifyError('Please Refresh The Page And Retry Again')
        
        if not client_uuid or client_uuid in ['null', 'undefined']:
            client_uuid = str(uuid.uuid4())

        customer_id= client_uuid   #Facebook App Scope ID Here
        customer_name= ''

        campaign = lib.util.verify.Verify.get_campaign(campaign_id)

        if models.cart.cart.Cart.objects.filter(customer_id = customer_id, campaign = campaign, platform = None,).exists():
            cart = models.cart.cart.Cart.objects.get(customer_id = customer_id, campaign = campaign, platform = None)
        else:
            
            cart = models.cart.cart.Cart.objects.create(
                customer_id = customer_id,
                customer_name = customer_name,
                campaign = campaign,
                platform = None,
                platform_id = None)

        cart_oid = database.lss.pre_order.get_oid_by_id(cart.id)
        
        response = JsonResponse({'client_uuid':client_uuid, 'cart_oid':cart_oid})
        response.set_cookie('client_uuid', client_uuid, path="/")

        return response

# ---------------------------------------------- buyer ------------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/(?P<login_with>[^/.]+)/buyer/create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_create_cart(self, request, campaign_id, login_with):

        api_user = lib.util.verify.Verify.get_customer_user(request)

        if login_with not in ['facebook','youtube','instagram']:
            customer_id = api_user.id
            customer_name= api_user.name
            customer_img= api_user.image
            # platform = 'lss'
        else:
            customer_id= getattr(api_user,f'{login_with}_info',{}).get('id')    #Facebook App Scope ID Here
            customer_name= getattr(api_user,f'{login_with}_info',{}).get('name')
            customer_img= getattr(api_user,f'{login_with}_info',{}).get('picture')
            # platform = login_with
            
        if not customer_id or not customer_name :
            raise lib.error_handle.error.api_error.ApiVerifyError('Invalid User')

        campaign = lib.util.verify.Verify.get_campaign(campaign_id)

        if models.cart.cart.Cart.objects.filter(customer_id = customer_id, campaign = campaign, platform = None,).exists():
            cart = models.cart.cart.Cart.objects.get(customer_id = customer_id, campaign = campaign, platform = None)
        else:
            
            cart = models.cart.cart.Cart.objects.create(
                customer_id = customer_id,
                customer_name = customer_name,
                campaign = campaign,
                platform = None,
                platform_id = None)

        cart_oid = database.lss.pre_order.get_oid_by_id(cart.id)
        return Response({ 'cart_oid':cart_oid}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<cart_oid>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_cart(self, request, cart_oid):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        # pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)

        if cart.buyer and cart.buyer != api_user:
            raise lib.error_handle.error.api_error.ApiVerifyError('Invalid User')

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_oid>[^/.]+)/buyer/checkout', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.cart_operation_error_handler.order_operation_error_handler
    def buyer_checkout_cart(self, request, cart_oid):
        
        shipping_data, = \
            lib.util.getter.getdata(request, ("shipping_data",), required=True)

        api_user = lib.util.verify.Verify.get_customer_user(request)
        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)

        rule.rule_checker.cart_rule_checker.CartCheckoutRuleChecker.check({'api_user':api_user, 'campaign':campaign, 'cart':cart})

        serializer =models.order.order.OrderSerializerUpdateShipping(data=shipping_data) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success, api_order = lib.helper.cart_helper.CartHelper.checkout(api_user, campaign.id, cart.id)


        if not success:
            cart = lib.util.verify.Verify.get_cart(cart.id)
            return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_205_RESET_CONTENT)

        order = lib.util.verify.Verify.get_order(api_order.id)

        serializer = models.order.order.OrderSerializerUpdateShipping(order, data=shipping_data, partial=True) 
        if not serializer.is_valid():
            data = models.order.order.OrderSerializer(order).data
            data['oid']=str(api_order._id)
            return Response(data, status=status.HTTP_200_OK)


        order = serializer.save()

        content = lib.helper.order_helper.OrderHelper.get_checkout_email_content(order,api_order._id)
        jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)     #queue this to redis if needed
        
        data = models.order.order.OrderSerializer(order).data
        data['oid']=str(api_order._id)
        
        # change buyer language
        api_user.lang = campaign.lang
        api_user.save()

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_oid>[^/.]+)/buyer/edit', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.cart_operation_error_handler.order_operation_error_handler
    def buyer_add_order_product(self, request, cart_oid):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        campaign_product_id, qty = lib.util.getter.getdata(request, ('campaign_product_id', 'qty',), required=True)

        if not qty or type(qty) != int :
            raise lib.error_handle.error.api_error.ApiVerifyError('qty_invalid')

        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)

        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
        campaign_product = campaign.products.get(id=campaign_product_id) if campaign.products.filter(id=campaign_product_id).exists() else None

        ret = rule.rule_checker.cart_rule_checker.CartEditProductRuleChecker.check(
            **{'cart':cart,'campaign':campaign, 'campaign_product_id':campaign_product_id, 'api_user':api_user, 'qty':qty})
        qty_difference = ret.get('qty_difference')

        database.lss.campaign_product.CampaignProduct(id=campaign_product.id).add_to_cart(qty_difference, sync=False)

        cart.products[campaign_product_id]={'qty':qty}
        cart.save()

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['DELETE'], url_path=r'(?P<cart_oid>[^/.]+)/buyer/delete',  permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.cart_operation_error_handler.order_operation_error_handler
    def buyer_delete_cart_product(self, request, cart_oid):


        campaign_product_id, = lib.util.getter.getdata(request, ('campaign_product_id', ), required=True)

        api_user = lib.util.verify.Verify.get_customer_user(request)
        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
        campaign_product = campaign.products.get(id=campaign_product_id) if campaign.products.filter(id=campaign_product_id).exists() else None


        rule.rule_checker.cart_rule_checker.CartDeleteProductRuleChecker.check({'api_user':api_user,'cart':cart,'campaign_product':campaign_product})

        if campaign_product_id not in cart.products:
            raise lib.error_handle.error.api_error.ApiVerifyError('campaign_product not found')
        
        qty = cart.products[campaign_product_id].get('qty',0)
        database.lss.campaign_product.CampaignProduct(id=campaign_product_id).customer_return(qty=qty, sync=False)

        del cart.products[campaign_product_id]
        cart.save()

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

# ---------------------------------------------- seller ------------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'seller/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_list_cart(self, request):

        api_user, campaign_id, search = lib.util.getter.getparams(request, ('campaign_id', 'search'), with_user=True, seller=True)

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        queryset = campaign.carts.exclude(products={}).order_by('id')

        if search:
            if search.isnumeric():
                queryset = queryset.filter(Q(id=int(search)) | Q(customer_name__icontains=search) )
            else:
                queryset = queryset.filter(customer_name__icontains=search)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = models.cart.cart.CartSerializer(page, many=True)
            result = self.get_paginated_response(
                serializer.data)
            data = result.data
        else:
            serializer = models.cart.cart.CartSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'seller/retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_retrieve_cart(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        cart = lib.util.verify.Verify.get_cart(pk)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, cart.campaign.id)

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'seller/retrieve/oid', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_retrieve_cart_oid(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        cart = lib.util.verify.Verify.get_cart(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, cart.campaign.id)
        oid = database.lss.cart.get_oid_by_id(cart.id)

        return Response(oid, status=status.HTTP_200_OK)


    @action(detail=True, methods=['PUT'], url_path=r'seller/adjust', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_update_adjust(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        adjust_list, = lib.util.getter.getdata(request, ('adjust_list',), required=True)
        cart = lib.util.verify.Verify.get_cart(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, cart.campaign.id)
        
        cart.seller_adjust = adjust_list
        cart.save()
        
        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)
    
    
    @action(detail=True, methods=['PUT'], url_path=r'seller/free/delivery', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_free_delivery(self, request, pk=None):

        free_delivery, = lib.util.getter.getdata(request, ('free_delivery',), required=True)

        if type(free_delivery) != bool :
            raise lib.error_handle.error.api_error.ApiVerifyError("request data error")

        api_user = lib.util.verify.Verify.get_seller_user(request)
        cart = lib.util.verify.Verify.get_cart(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, cart.campaign.id)

        cart.free_delivery = free_delivery
        cart.save()

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)
        