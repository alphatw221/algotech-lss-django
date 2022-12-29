
from django.http import HttpResponseRedirect
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from automation import jobs
from api import models
import lib
import database
import service

from datetime import datetime

class TikTokViewSet(viewsets.GenericViewSet):
    queryset = models.twitch.twitch_channel.TwitchChannel.objects.none()

    @action(detail=False, methods=['POST'], url_path=r'comment/process/(?P<campaign_id>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def process_tiktok_live_comments(self, request, campaign_id):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)


        # if 'tiktok' not in user_subscription.user_plan.get('activated_platform'):
        #     raise lib.error_handle.error.api_error.ApiVerifyError('tiktok_not_activated')
        


        service.rq.queue.enqueue_campaign_queue(jobs.comment_create_job.comment_create_job, campaign_id = campaign.id, comments = request.data, platform='tiktok', push_comment = True)

        return Response({'message': 'enqueue success'}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/cart', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_campaign_tiktok_cart(self, request, campaign_id):

        data = {'request_at':datetime.utcnow().timestamp()}

        tiktok_auth_url = 'https://www.tiktok.com/auth/authorize/'
        scope = 'user.info.basic'
        # https://7dde-58-115-116-33.jp.ngrok.io/api/v2/tiktok/1234/cart
        # redirect_uri = f'https://7dde-58-115-116-33.jp.ngrok.io/api/v2/tiktok/{campaign_id}/cart/auth/callback/'
        redirect_uri = f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/tiktok/{campaign_id}/cart/auth/callback/'
        state = lib.util.crypto.encode(data)
        response_type = 'code'

        return HttpResponseRedirect(
            redirect_to=f'{tiktok_auth_url}?client_key={settings.TIKTOK_CLIENT_KEY}&scope={scope}&redirect_uri={redirect_uri}&state={state}&response_type={response_type}')
    

    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/cart/auth/callback', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_campaign_tiktok_cart_auth_callback(self, request, campaign_id):

        code, scopes, state, error = lib.util.getter.getparams(request, ('code', 'scopes', 'state', 'error'), with_user=False)

        if lib.util.crypto.decode(state).get('request_at',1)+60 < datetime.utcnow().timestamp():
            error_message = 'please_try_again'
            return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/search/{campaign_id}/cart/tiktok?message={error_message}')

        success, response = service.tiktok.user.get_user_token_with_code(code)
        access_token = response.get('data',{}).get('access_token')
        
        if not success or not access_token:
            error_message = 'please_try_again'
            return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/search/{campaign_id}/cart/tiktok?message={error_message}')

        

        success, response = service.tiktok.user.get_user_info(access_token, fields='display_name,open_id,union_id,avatar_url')
        display_name = response.get('data',{}).get('user',{}).get('display_name')
        if not success or not display_name:
            error_message = 'please_try_again'
            return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/search/{campaign_id}/cart/tiktok?message={error_message}')

        

        if not models.cart.cart.Cart.objects.filter(campaign_id=campaign_id, customer_name=display_name, platform=models.user.user_subscription.PLATFORM_TIKTOK).exists():
            error_message = 'cart_not_found'
            return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/search/{campaign_id}/cart/tiktok?message={error_message}')


        cart = models.cart.cart.Cart.objects.filter(campaign_id=campaign_id, customer_name=display_name, platform=models.user.user_subscription.PLATFORM_TIKTOK).first()
        oid = database.lss.cart.get_oid_by_id(cart.id)


        response = HttpResponseRedirect(
            redirect_to=f'{settings.SHOPPING_CART_URL}/{oid}')

        return response
    


    # @action(detail=False, methods=['GET'], url_path=r'auth', permission_classes=())
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def tiktok_auth(self, request):

    #     request_from = ''
    #     timestamp = 123456

    #     tiktok_auth_url = 'https://www.tiktok.com/auth/authorize/'
    #     client_key = 'aw8ec3na0zh867am'
    #     scope = 'user.info.basic'
    #     redirect_uri = f'https://v1login.liveshowseller.com/api/v2/tiktok/auth/callback/'
    #     # redirect_uri = f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/tiktok/{campaign_id}/cart/auth/callback/'
    #     state = 'encription'
    #     response_type = 'code'

    #     return HttpResponseRedirect(
    #         redirect_to=f'{tiktok_auth_url}?client_key={client_key}&scope={scope}&redirect_uri={redirect_uri}&state={state}&response_type={response_type}')
    

    