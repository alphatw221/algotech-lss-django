from re import S
from django.http import JsonResponse
from django.db.models import Q, Value

from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action

from api import models
from api import rule

from automation import jobs

import lib
from datetime import datetime
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
    permission_classes = (IsAdminUser,)
# ---------------------------------------------- guest ------------------------------------------------------
    # @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<cart_oid>[^/.]+)/platform', permission_classes=(), authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def guest_retrieve_cart_platform(self, request, cart_oid):
    #     cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
    #     return Response(cart.platform, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<cart_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def guest_retrieve_cart(self, request, cart_oid):
    #     cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)

    #     return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_oid>[^/.]+)/guest/product/edit', permission_classes=(), authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # @lib.error_handle.error_handler.cart_operation_error_handler.update_cart_product_error_handler
    # def guest_edit_cart_product(self, request, cart_oid):

    #     campaign_product_id, qty = lib.util.getter.getdata(request, ('campaign_product_id', 'qty',), required=True)

    #     cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
    #     campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
    #     campaign_product = campaign.products.get(id=campaign_product_id) if campaign.products.filter(id=campaign_product_id).exists() else None

    #     ret = rule.rule_checker.cart_rule_checker.CartEditProductRuleChecker.check(
    #         **{'cart':cart,'campaign':campaign, 'campaign_product_id':campaign_product_id, 'api_user':None, 'qty':qty})
    #     qty_difference = ret.get('qty_difference')

    #     database.lss.campaign_product.CampaignProduct(id=campaign_product.id).add_to_cart(qty_difference, sync=False)

    #     cart.products[campaign_product_id]={'qty':qty}
    #     cart.save()

    #     return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['DELETE'], url_path=r'(?P<cart_oid>[^/.]+)/guest/product/delete', permission_classes=(), authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # @lib.error_handle.error_handler.cart_operation_error_handler.update_cart_product_error_handler
    # def guest_delete_cart_product(self, request, cart_oid):

    #     campaign_product_id, = lib.util.getter.getdata(request, ('campaign_product_id', ), required=True)

    #     cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
    #     campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
    #     campaign_product = campaign.products.get(id=campaign_product_id) if campaign.products.filter(id=campaign_product_id).exists() else None


    #     rule.rule_checker.cart_rule_checker.CartDeleteProductRuleChecker.check({'api_user':None,'cart':cart,'campaign_product':campaign_product})

    #     if campaign_product_id not in cart.products:
    #         raise lib.error_handle.error.api_error.ApiVerifyError('campaign_product_not_found')
        
    #     qty = cart.products[campaign_product_id].get('qty',0)
    #     database.lss.campaign_product.CampaignProduct(id=campaign_product_id).customer_return(qty=qty, sync=False)

    #     del cart.products[campaign_product_id]
    #     cart.save()

    #     return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_oid>[^/.]+)/guest/checkout', permission_classes=(), authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # @lib.error_handle.error_handler.cart_operation_error_handler.update_cart_product_error_handler
    # def guest_checkout_cart(self, request, cart_oid):
        
    #     shipping_data, = \
    #         lib.util.getter.getdata(request, ("shipping_data",), required=True)

    #     cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
    #     campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)

    #     rule.rule_checker.cart_rule_checker.CartCheckoutRuleChecker.check({'api_user':None, 'campaign':campaign, 'cart':cart})

    #     serializer = models.order.order.OrderSerializerUpdateShipping(data=shipping_data) 
    #     if not serializer.is_valid():
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #     #checkout
    #     success, api_order = lib.helper.cart_helper.CartHelper.checkout(None, campaign.id, cart.id)


    #     if not success:
    #         cart = lib.util.verify.Verify.get_cart(cart.id)
    #         return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_205_RESET_CONTENT)

    #     order = lib.util.verify.Verify.get_order(api_order.id)

    #     serializer = models.order.order.OrderSerializerUpdateShipping(order, data=shipping_data, partial=True) 
    #     if not serializer.is_valid():
    #         data = models.order.order.OrderSerializer(order).data
    #         data['oid']=str(api_order._id)
    #         return Response(data, status=status.HTTP_200_OK)

    #     order = serializer.save()

    #     content = lib.helper.order_helper.OrderHelper.get_checkout_email_content(order,api_order._id)
    #     jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)     #queue this to redis if needed
        
    #     data = models.order.order.OrderSerializer(order).data
    #     data['oid']=str(api_order._id)

    #     #send email to customer over here order detail link
    #     return Response(data, status=status.HTTP_200_OK)




    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/guest/create', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_create_cart(self, request, campaign_id):

        recaptcha_token, client_uuid = lib.util.getter.getparams(request, ('recaptcha_token', 'client_uuid'), with_user=False)
        
        code, response = service.recaptcha.recaptcha.verify_token(recaptcha_token)

        if code!=200 or not response.get('success'):
            raise lib.error_handle.error.api_error.ApiVerifyError('refresh_try_again')
        
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

        cart_oid = database.lss.cart.get_oid_by_id(cart.id)
        
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
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_user')

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

        cart_oid = database.lss.cart.get_oid_by_id(cart.id)
        return Response({ 'cart_oid':cart_oid}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<cart_oid>[^/.]+)', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_cart(self, request, cart_oid):


        api_user = lib.util.verify.Verify.get_customer_user(request) if request.user.is_authenticated else None
        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        # pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)

        if cart.buyer and cart.buyer != api_user:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_user')

        return Response(models.cart.cart.CartSerializerWithUserSubscription(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_oid>[^/.]+)/buyer/checkout', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.cart_operation_error_handler.update_cart_product_error_handler
    def buyer_checkout_cart(self, request, cart_oid):
        
        shipping_data, = \
            lib.util.getter.getdata(request, ("shipping_data",), required=True)

        api_user = lib.util.verify.Verify.get_customer_user(request) if request.user.is_authenticated else None
        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)

        rule.rule_checker.cart_rule_checker.RuleChecker.check(
            check_list=[
                rule.rule_checker.cart_rule_checker.CartCheckRule.allow_checkout,
                rule.rule_checker.cart_rule_checker.CartCheckRule.is_cart_lock,
                rule.rule_checker.cart_rule_checker.CartCheckRule.is_cart_empty
            ],
            **{'api_user':api_user, 'campaign':campaign, 'cart':cart}
        )


        serializer =models.order.order.OrderSerializerUpdateShipping(data=shipping_data) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        campaign_product_dict = database.lss_cache.campaign_product.get_product_dict(campaign_id=campaign.id, bypass=True)
        success, pymongo_order = lib.helper.cart_helper.CartHelper.checkout(api_user, campaign.id, cart.id, campaign_product_dict=campaign_product_dict)
        
        if not success:
            cart = lib.util.verify.Verify.get_cart(cart.id)
            return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_205_RESET_CONTENT)
        
        order = lib.util.verify.Verify.get_order(pymongo_order.id)
        order_oid = str(pymongo_order._id)
        serializer = models.order.order.OrderSerializerUpdateShipping(order, data=shipping_data, partial=True) 
        if not serializer.is_valid():
            data = models.order.order.OrderWithCampaignSerializer(order).data
            data['oid']=order_oid
            return Response(data, status=status.HTTP_200_OK)


        order = serializer.save()
        lib.helper.order_helper.OrderHelper.summarize_order(order, save=False)
        order.buyer = api_user
        order.save()
        
        
        subject = lib.i18n.email.cart_checkout_mail.i18n_get_mail_subject(order=order, lang=order.campaign.lang) 
        content = lib.i18n.email.cart_checkout_mail.i18n_get_mail_content(order, order_oid, lang=order.campaign.lang) 
        jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)  
        
        data = models.order.order.OrderWithCampaignSerializer(order).data
        data['oid']=order_oid
        
        #discount used
        if type(order.applied_discount.get('id'))==int and models.discount_code.discount_code.DiscountCode.objects.filter(id=order.applied_discount.get('id')).exists():
            discount_code = models.discount_code.discount_code.DiscountCode.objects.get(id=order.applied_discount.get('id'))
            discount_code.used_count+=1
            discount_code.save()
            
        # change buyer language
        if request.user.is_authenticated:
            api_user.lang = campaign.lang
            api_user.save()

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_oid>[^/.]+)/buyer/product/edit', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.cart_operation_error_handler.update_cart_product_error_handler
    def buyer_edit_cart_product(self, request, cart_oid):

        api_user = lib.util.verify.Verify.get_customer_user(request) if request.user.is_authenticated else None
        campaign_product_id, qty = lib.util.getter.getdata(request, ('campaign_product_id', 'qty',), required=True)

        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)

        rule.rule_checker.cart_rule_checker.RuleChecker.check(check_list=[
            rule.check_rule.cart_check_rule.CartCheckRule.campaign_product_type,
        ],**{
            'api_user':api_user,
            'campaign_product':campaign_product,
        })

        lib.helper.cart_helper.CartHelper.update_cart_product(api_user, cart, campaign_product, qty)

        cart = lib.util.verify.Verify.get_cart(cart.id)
        # ret = rule.rule_checker.cart_rule_checker.CartEditProductRuleChecker.check(
        #     **{'cart':cart,'campaign':campaign, 'campaign_product_id':campaign_product_id, 'api_user':api_user, 'qty':qty})
        # qty_difference = ret.get('qty_difference')

        # database.lss.campaign_product.CampaignProduct(id=campaign_product.id).add_to_cart(qty_difference, sync=False)

        # cart.products[campaign_product_id]={'qty':qty}
        # cart.save()

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['DELETE'], url_path=r'(?P<cart_oid>[^/.]+)/buyer/product/delete',  permission_classes=())
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def buyer_delete_cart_product(self, request, cart_oid):


    #     campaign_product_id, = lib.util.getter.getdata(request, ('campaign_product_id', ), required=True)

    #     api_user = lib.util.verify.Verify.get_customer_user(request) if request.user.is_authenticated else None
    #     cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
    #     campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
    #     campaign_product = campaign.products.get(id=campaign_product_id) if campaign.products.filter(id=campaign_product_id).exists() else None

    #     lib.helper.cart_helper.CartHelper.update_cart_product(api_user, cart, campaign_product, 0, campaign)
    #     # rule.rule_checker.cart_rule_checker.CartDeleteProductRuleChecker.check({'api_user':api_user,'cart':cart,'campaign_product':campaign_product})

    #     # if campaign_product_id not in cart.products:
    #     #     raise lib.error_handle.error.api_error.ApiVerifyError('campaign_product_not_found')
        
    #     # qty = cart.products[campaign_product_id].get('qty',0)
    #     # database.lss.campaign_product.CampaignProduct(id=campaign_product_id).customer_return(qty=qty, sync=False)

    #     # del cart.products[campaign_product_id]
    #     # cart.save()

    #     return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_oid>[^/.]+)/buyer/discount',  permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_apply_discount_code(self, request, cart_oid):

        discount_code, = \
            lib.util.getter.getdata(request, ("discount_code",), required=True)

        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)

        discount_codes = campaign.user_subscription.discount_codes.filter(start_at__lte=datetime.utcnow(),end_at__gte=datetime.utcnow())

        valid_discount_code = None
        for _discount_code in discount_codes:

            if _discount_code.type ==models.discount_code.discount_code.TYPE_GENERAL and discount_code == _discount_code.code:
                valid_discount_code = _discount_code
                break
            elif _discount_code.type == models.discount_code.discount_code.TYPE_CART_REFERAL :
                code_length = len(_discount_code.code)
                if code_length+1 > len(discount_code) or _discount_code.code!=discount_code[:code_length]:
                    continue
                cart_oid = discount_code[code_length+1:]
                try:
                    referrer_cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
                    # referrer_pre_order=lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
                except Exception:
                    break
                if referrer_cart.campaign.user_subscription != campaign.user_subscription or referrer_cart == cart:
                    continue
                if not referrer_cart.applied_discount and lib.helper.discount_helper.CartDiscountHelper.check_limitations(_discount_code.limitations, cart = referrer_cart, discount_code = _discount_code) :
                    discount_code_data = _discount_code.__dict__.copy()
                    del discount_code_data['_state']
                    referrer_cart.applied_discount = discount_code_data
                    referrer_cart.save()
                valid_discount_code = _discount_code
                break

        if not valid_discount_code:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_discount_code')
        
        for limitation in valid_discount_code.limitations:
            if not lib.helper.discount_helper.CartDiscountHelper.check_limitation(limitation, cart=cart, discount_code=valid_discount_code):
                raise lib.error_handle.error.api_error.ApiVerifyError('not_eligible')

        discount_code_data = valid_discount_code.__dict__.copy()
        del discount_code_data['_state']
        cart.applied_discount = discount_code_data
        lib.helper.discount_helper.CartDiscountHelper.make_discount(cart)
        cart.save()

        valid_discount_code.applied_count+=1
        valid_discount_code.save()

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['DELETE'], url_path=r'(?P<cart_oid>[^/.]+)/buyer/discount/cancel',  permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_cancel_discount_code(self, request, cart_oid):

        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
        
        if models.discount_code.discount_code.DiscountCode.objects.filter(id=cart.applied_discount.get('id')).exists():
            discount_code = models.discount_code.discount_code.DiscountCode.objects.get(id=cart.applied_discount.get('id'))
            discount_code.applied_count-=1
            discount_code.applied_count = max(discount_code.applied_count,0)
            discount_code.save()

        cart.applied_discount = {}
        cart.discount = 0
        cart.save()

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

# ---------------------------------------------- seller ------------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'seller/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_list_cart(self, request):
        try:
            api_user, campaign_id = lib.util.getter.getparams(request, ('campaign_id',), with_user=True, seller=True)
            user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
            campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
            queryset = campaign.carts.exclude(products=Value('null')).order_by('id')

            serializer = models.cart.cart.CartSerializer(queryset, many=True)
            data = serializer.data

            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            import traceback
            print(traceback.format_exc())
            
    @action(detail=False, methods=['GET'], url_path=r'seller/search', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_search_cart(self, request):

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

    @action(detail=False, methods=['PUT'], url_path=r'(?P<cart_id>[^/.]+)/seller/product/edit', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.cart_operation_error_handler.update_cart_product_error_handler
    def seller_edit_cart_product(self, request, cart_id):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        campaign_product_id, qty = lib.util.getter.getdata(request, ('campaign_product_id', 'qty',), required=True)

        cart = lib.util.verify.Verify.get_cart(cart_id)
        campaign = lib.util.verify.Verify.get_campaign_from_cart(cart)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)

        lib.helper.cart_helper.CartHelper.update_cart_product(api_user, cart, campaign_product, qty)
        cart = lib.util.verify.Verify.get_cart(cart.id)
        # ret = rule.rule_checker.cart_rule_checker.CartEditProductRuleChecker.check(
        #     **{'cart':cart,'campaign':campaign, 'campaign_product_id':campaign_product_id, 'api_user':api_user, 'qty':qty})
        # qty_difference = ret.get('qty_difference')

        # database.lss.campaign_product.CampaignProduct(id=campaign_product.id).add_to_cart(qty_difference, sync=False)

        # cart.products[campaign_product_id]={'qty':qty}
        # cart.save()

        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['PUT'], url_path=r'seller/adjust', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def seller_update_adjust(self, request, pk=None):

    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     adjust_list, = lib.util.getter.getdata(request, ('adjust_list',), required=True)
    #     cart = lib.util.verify.Verify.get_cart(pk)
    #     lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, cart.campaign.id)
        
    #     cart.seller_adjust = adjust_list
    #     cart.save()
        
    #     return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)
    
    
    # @action(detail=True, methods=['PUT'], url_path=r'seller/free/delivery', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def seller_free_delivery(self, request, pk=None):

    #     free_delivery, = lib.util.getter.getdata(request, ('free_delivery',), required=True)

    #     if type(free_delivery) != bool :
    #         raise lib.error_handle.error.api_error.ApiVerifyError("request_data_error")

    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     cart = lib.util.verify.Verify.get_cart(pk)
    #     lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, cart.campaign.id)

    #     cart.free_delivery = free_delivery
    #     cart.save()

    #     return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['PUT'], url_path=r'seller/adjust', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_adjust(self, request, pk=None):

        adjust_price, adjust_title, free_delivery = lib.util.getter.getdata(request, ('adjust_price', 'adjust_title', 'free_delivery'))
        if type(adjust_price) not in [int, float, None]:
            raise lib.error_handle.error.api_error.ApiVerifyError("request_data_error")


        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        cart = lib.util.verify.Verify.get_cart(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, cart.campaign.id)

        cart.free_delivery = bool(free_delivery)
        cart.adjust_title = adjust_title

        adjust_price = 0 if not adjust_price else adjust_price
        cart.adjust_price = float(adjust_price)

        cart.save()
        
        return Response(models.cart.cart.CartSerializer(cart).data, status=status.HTTP_200_OK)