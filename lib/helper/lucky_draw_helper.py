import pickle
import platform
import time
from typing import OrderedDict
import functools, logging, traceback
from api import models
import service
from django.conf import settings
import os
import random
import lib
from api import models
from collections import OrderedDict
from django.db.models import Q, Value

import database
class LuckyDrawCandidate():

    def __init__(self,platform, customer_id, comment_id=None, customer_name="", customer_image="", draw_type=None, prize=None):
        self.comment_id = comment_id
        self.platform = platform
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_image = customer_image
        self.draw_type = draw_type
        self.prize = prize

    def __hash__(self) -> int:
        return (self.platform, self.customer_id).__hash__()


    def __eq__(self, __o: object) -> bool:
        try:
            if type(__o) in [dict,OrderedDict]:
                return self.platform ==__o.get('platform') and self.customer_id==__o.get('customer_id')
            return self.platform == __o.platform and self.customer_id==__o.customer_id
        except Exception:
            return False

    def to_dict(self):
        return {'platform':self.platform,'customer_id':self.customer_id,'customer_name':self.customer_name,'customer_image':self.customer_image,'draw_type':self.draw_type,'prize':self.prize}

class CandidateSetGenerator():

    @classmethod
    def get_candidate_set(cls):
        return set()


class KeywordCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw, limit=1000):
        
        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()
        campaign_comments = models.campaign.campaign_comment.CampaignComment.objects.filter(
            campaign=campaign,
            # message=keyword,
            message__contains=lucky_draw.comment,
        )[:limit]

        for campaign_comment in campaign_comments:

            candidate = LuckyDrawCandidate(
                platform=campaign_comment.platform, 
                customer_id=campaign_comment.customer_id, 
                comment_id = campaign_comment.id,
                customer_name=campaign_comment.customer_name,
                customer_image=campaign_comment.image,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set

class CommentCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw, limit=1000):
        
        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()
        campaign_comments = models.campaign.campaign_comment.CampaignComment.objects.filter(
            campaign=campaign,
        )[:limit]

        for campaign_comment in campaign_comments:

            candidate = LuckyDrawCandidate(
                platform=campaign_comment.platform, 
                customer_id=campaign_comment.customer_id, 
                comment_id = campaign_comment.id,
                customer_name=campaign_comment.customer_name,
                customer_image=campaign_comment.image,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set


class LikesCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw, limit=1000):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()
        
        likes_user_list=[]
        response = {}
        
        if campaign.facebook_page_id and models.facebook.facebook_page.FacebookPage.objects.filter(id=campaign.facebook_page_id).exists():
            facebook_page = models.facebook.facebook_page.FacebookPage.objects.get(id=campaign.facebook_page_id)
            post_id=campaign.facebook_campaign.get('post_id')
            token=facebook_page.token   

            code, response = service.facebook.post.get_post_likes(token, facebook_page.page_id, post_id, after=None, limit=limit)
            # print(code)
            # print(response)
            if code!=200 :
                raise lib.error_handle.error.api_error.ApiVerifyError('helper.fb_api_fail')
            # likes_user_list += [user.get('name') for user in response.get('data',[])]
            # print(likes_user_list)
        # campaign_comments = models.campaign.campaign_comment.CampaignComment.objects.filter(
        #     campaign=campaign,
        #     customer_name__in=likes_user_list
        # )[:limit]

        for user in response.get('data',[]):
        
            candidate = LuckyDrawCandidate(
                platform='facebook', 
                customer_id=user.get('id'),     #ASID over here!! might have some issues 
                customer_name=user.get('name'),
                customer_image=user.get('pic_large'),
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set



class ProductCandidateSetGenerator(CandidateSetGenerator):
    
    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()


        orders = models.order.order.Order.objects.filter(campaign=campaign, platform__isnull=False, products__has_key=str(lucky_draw.campaign_product.id))
        carts = models.cart.cart.Cart.objects.filter(campaign=campaign, platform__isnull=False, products__has_key=str(lucky_draw.campaign_product.id))
        for order in orders:
            candidate = LuckyDrawCandidate(
                platform=order.platform, 
                customer_id=order.customer_id, 
                customer_name=order.customer_name,
                customer_image=order.customer_img,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)
        
        for cart in carts:
            candidate = LuckyDrawCandidate(
                platform=cart.platform, 
                customer_id=cart.customer_id, 
                customer_name=cart.customer_name,
                customer_image=cart.customer_img,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)
        print(candidate_set)
        return candidate_set


class PurchaseCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()

        orders = models.order.order.Order.objects.filter(campaign=campaign, platform__isnull=False)
        carts = models.cart.cart.Cart.objects.filter(campaign=campaign, platform__isnull=False).exclude(products=Value('null'))

        for order in orders:
            candidate = LuckyDrawCandidate(
                platform=order.platform, 
                customer_id=order.customer_id, 
                customer_name=order.customer_name,
                customer_image=order.customer_img,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)
        
        for cart in carts:
            candidate = LuckyDrawCandidate(
                platform=cart.platform, 
                customer_id=cart.customer_id, 
                customer_name=cart.customer_name,
                customer_image=cart.customer_img,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)
        print(candidate_set)
        return candidate_set

class SharedPostCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw, limit=1000):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()
        users_like_and_comment_set = set()
        response = {}
        
        if campaign.facebook_page_id and models.facebook.facebook_page.FacebookPage.objects.filter(id=campaign.facebook_page_id).exists():
            facebook_page = models.facebook.facebook_page.FacebookPage.objects.get(id=campaign.facebook_page_id)
            post_id=campaign.facebook_campaign.get('post_id')
            token=facebook_page.token   

            code, response = service.facebook.post.get_post(token, facebook_page.page_id, post_id)
            if code!=200 :
                raise lib.error_handle.error.api_error.ApiVerifyError('helper.fb_api_fail')
        
        shares_count = response.get("shares", {}).get("count", 0)
        # print(shares_count)
        if not shares_count:
            return candidate_set
        
        
        shared_user_name_set = set(lucky_draw.meta.get("shared_post_data", {}))
        print("shared_user_name_set", shared_user_name_set)
        if not shared_user_name_set:
            return candidate_set
        
        like_data = response.get("likes",{}).get("data",[])
        # print(like_data)
        like_user_id_set = set([i["id"] for i in like_data])
        
        comments_data = models.campaign.campaign_comment.CampaignComment.objects.filter(
            campaign=campaign, platform="facebook")
        # campaign_comments_user_id_set = set(comments_data.values_list("customer_id", flat=True))
        campaign_comments_user_name_set = set(comments_data.values_list("customer_name", flat=True))
        print("campaign_comments_user_name_set", campaign_comments_user_name_set)
        
        if len(campaign_comments_user_name_set):
            users_shared_and_comment_set = shared_user_name_set.intersection(campaign_comments_user_name_set)
            campaign_comments = comments_data.filter(customer_name__in=list(users_shared_and_comment_set))
            for campaign_comment in campaign_comments:
                candidate = LuckyDrawCandidate(
                    platform=campaign_comment.platform, 
                    customer_id=campaign_comment.customer_id, 
                    comment_id = campaign_comment.id,
                    customer_name=campaign_comment.customer_name,
                    customer_image=campaign_comment.image,
                    draw_type=lucky_draw.type,
                    prize=lucky_draw.prize.name)

                if not lucky_draw.repeatable and candidate in winner_list:
                    continue

                candidate_set.add(candidate)
        
        # if len(like_user_id_set) and len(campaign_comments_user_id_set):
        #     users_like_and_comment_set = like_user_id_set.intersection(campaign_comments_user_id_set)
        #     data = []
        #     for i in like_data:
        #         if i["id"] in users_like_and_comment_set and i["id"] not in data:
        #             data.append(i)
        #     for user in data:
        #         candidate = LuckyDrawCandidate(
        #             platform='facebook', 
        #             customer_id=user.get('id'),     #ASID over here!! might have some issues 
        #             customer_name=user.get('name'),
        #             customer_image=user.get('pic_large'),
        #             draw_type=lucky_draw.type,
        #             prize=lucky_draw.prize.name)

        #         if not lucky_draw.repeatable and candidate in winner_list:
        #             continue
                
        #         candidate_set.add(candidate)
                
        # elif not len(like_user_id_set) and not len(campaign_comments_user_id_set):
        #     return candidate_set
        
        # elif len(like_user_id_set):
        #     users_like_and_comment_set = like_user_id_set
        #     data = []
        #     for i in like_data:
        #         if i["id"] in users_like_and_comment_set and i["id"] not in data:
        #             data.append(i)
        #     for user in data:
        #         candidate = LuckyDrawCandidate(
        #             platform='facebook', 
        #             customer_id=user.get('id'),     #ASID over here!! might have some issues 
        #             customer_name=user.get('name'),
        #             customer_image=user.get('pic_large'),
        #             draw_type=lucky_draw.type,
        #             prize=lucky_draw.prize.name)

        #         if not lucky_draw.repeatable and candidate in winner_list:
        #             continue
        #         candidate_set.add(candidate)
                
        # elif len(campaign_comments_user_id_set):
        #     users_like_and_comment_set = campaign_comments_user_id_set
        #     campaign_comments = []
        #     for i in comments_data:
        #         if i.id in users_like_and_comment_set and i.id not in campaign_comments:
        #             campaign_comments.append(i)
        #     for campaign_comment in campaign_comments:

        #         candidate = LuckyDrawCandidate(
        #             platform=campaign_comment.platform, 
        #             customer_id=campaign_comment.customer_id, 
        #             comment_id = campaign_comment.id,
        #             customer_name=campaign_comment.customer_name,
        #             customer_image=campaign_comment.image,
        #             draw_type=lucky_draw.type,
        #             prize=lucky_draw.prize.name)

        #         if not lucky_draw.repeatable and candidate in winner_list:
        #             continue

        #         candidate_set.add(candidate)
        
        num_of_candidate = len(candidate_set) if shares_count > len(candidate_set) else shares_count
        candidates = random.sample(list(candidate_set), num_of_candidate)
        return candidates
    
class LuckyDraw():

    @classmethod
    def draw_from_candidate(cls, campaign, campaign_product, candidate_set=set(), num_of_winner=1, api_user=None):
        if not candidate_set:
            print('no candidate')
            return []
        num_of_winner = len(candidate_set) if num_of_winner > len(candidate_set) else num_of_winner
        winners = random.sample(list(candidate_set), num_of_winner)
        if not winners:
            print('no winners')
            return []
        
        campaign_winner_list = campaign.meta.get('winner_list',[])
        winner_list = []

        
        for winner in winners:                                              #multithread needed
            try:
                cls.__add_product(campaign, winner, campaign_product, api_user)
                cls.__announce(campaign, winner, campaign_product)
                cls.__send_private_message(campaign, winner, campaign_product)
                winner_dict = winner.to_dict()
                # if winner not in campaign_winner_list:
                campaign_winner_list.append(winner_dict)

                winner_list.append(winner_dict)
            except Exception:
                import traceback
                print(traceback.format_exc())
                pass
            
        campaign.meta['winner_list']=campaign_winner_list
        campaign.save()

        return winner_list

    @classmethod
    def __add_product(
        cls, 
        campaign: models.campaign.campaign.Campaign, 
        winner:LuckyDrawCandidate, 
        campaign_product:models.campaign.campaign_product.CampaignProduct ,
        api_user
        ):

            if models.cart.cart.Cart.objects.filter(
                campaign=campaign, platform=winner.platform, customer_id=winner.customer_id, customer_name=winner.customer_name).exists():
                cart = models.cart.cart.Cart.objects.get(
                    campaign=campaign, platform=winner.platform, customer_id=winner.customer_id, customer_name=winner.customer_name)
            else:
                platform_id_dict = {
                    'facebook': campaign.facebook_page.id if campaign.facebook_page else None,
                    'youtube': campaign.youtube_channel.id if campaign.youtube_channel else None,
                    'instagram': campaign.instagram_profile.id if campaign.instagram_profile else None
                }
                cart = models.cart.cart.Cart.objects.create(
                    customer_id=winner.customer_id, 
                    customer_name=winner.customer_name, 
                    customer_img=winner.customer_image, 
                    campaign = campaign, 
                    user_subscription = campaign.user_subscription,
                    platform=winner.platform, 
                    platform_id=platform_id_dict.get(winner.platform))


            if  str(campaign_product.id) in cart.products:
                qty = cart.products.get(str(campaign_product.id),0)+1
            else :
                qty = 1
            lib.helper.cart_helper.CartHelper.update_cart_product(api_user=api_user, cart=cart, campaign_product=campaign_product, qty=qty)
            # if prize_product := pre_order.products.get(str(campaign_product.id), None):
            #     qty = prize_product['qty'] + 1
            #     lib.helper.order_helper.PreOrderHelper.update_product(api_user=None, pre_order_id=pre_order.id, 
            #         order_product_id=prize_product.get('order_product_id'),qty=qty)
            # else:
            #     lib.helper.order_helper.PreOrderHelper.add_product(api_user=None, pre_order_id=pre_order.id, campaign_product_id=campaign_product.id,qty=1)
            
    

    @classmethod
    def __announce(cls, 
    campaign: models.campaign.campaign.Campaign, 
    winner: LuckyDrawCandidate, 
    campaign_product:models.campaign.campaign_product.CampaignProduct):
        
        if lucky_draw_announce:=campaign.meta_reply.get('lucky_draw_announce'):
            lucky_draw_announce = lucky_draw_announce.replace('[CUSTOMER_NAME]', winner.customer_name)
            lucky_draw_announce = lucky_draw_announce.replace('[PRIZE_NAME]', campaign_product.name)
            text = lucky_draw_announce
        else:
            text = lib.i18n.campaign_announcement.get_campaign_announcement_lucky_draw_winner(campaign_product.name, winner.customer_name, lang=campaign.lang)


        if (facebook_page := campaign.facebook_page):
            service.facebook.post.post_page_comment_on_post(facebook_page.token, campaign.facebook_campaign.get('post_id'), text)
        

        if (youtube_channel := campaign.youtube_channel):
            service.youtube.live_chat.post_live_chat_comment(youtube_channel.token, campaign.youtube_campaign.get('live_chat_id'), text)

    @classmethod
    def __send_private_message(
            cls, 
            campaign: models.campaign.campaign.Campaign, 
            winner: LuckyDrawCandidate, 
            campaign_product:models.campaign.campaign_product.CampaignProduct
        ):


        if lucky_draw_announce:=campaign.meta_reply.get('lucky_draw_private_message'):
            lucky_draw_announce = lucky_draw_announce.replace('[CUSTOMER_NAME]', winner.customer_name)
            lucky_draw_announce = lucky_draw_announce.replace('[PRIZE_NAME]', campaign_product.name)
            text = lucky_draw_announce
        else:
            text = lib.i18n.campaign_announcement.get_campaign_announcement_lucky_draw_winner(campaign_product.name, winner.customer_name, lang=campaign.lang)  #temp

        if (campaign.instagram_profile and winner.platform=='instagram'):
            service.instagram.chat_bot.post_page_message_chat_bot(campaign.instagram_profile.connected_facebook_page_id, campaign.instagram_profile.token, winner.customer_id, text)

        if (campaign.facebook_page and winner.platform=='facebook' and winner.comment_id):
            service.facebook.post.post_page_message_on_comment(campaign.facebook_page.token, winner.comment_id, text)
    
    @classmethod
    def __get_image(cls, winner:LuckyDrawCandidate):
        pass



def draw(campaign, lucky_draw, api_user):
    
    if lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_KEYWORD:
        candidate_set = lib.helper.lucky_draw_helper.KeywordCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_LIKE:
        candidate_set = lib.helper.lucky_draw_helper.LikesCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_PRODUCT:
        candidate_set = lib.helper.lucky_draw_helper.ProductCandidateSetGenerator.get_candidate_set(campaign, lucky_draw)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_PURCHASE:
        candidate_set = lib.helper.lucky_draw_helper.PurchaseCandidateSetGenerator.get_candidate_set(campaign, lucky_draw)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_LIKE_AND_COMMENT:

        fb_like_candidate_set = lib.helper.lucky_draw_helper.LikesCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
        comment_candidate_set = lib.helper.lucky_draw_helper.CommentCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
        candidate_set = fb_like_candidate_set.intersection(comment_candidate_set)
    
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_POST:
        candidate_set = lib.helper.lucky_draw_helper.SharedPostCandidateSetGenerator.get_candidate_set(campaign, lucky_draw)
    else:
        return []
    return lib.helper.lucky_draw_helper.LuckyDraw.draw_from_candidate(campaign, lucky_draw.prize,  candidate_set=candidate_set, num_of_winner=lucky_draw.num_of_winner, api_user=api_user)


