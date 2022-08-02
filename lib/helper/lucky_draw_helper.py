from typing import OrderedDict
from api import models
import service

import random
import lib
from api import models
from collections import OrderedDict


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


class LikesCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw, limit=1000):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()
        
        likes_user_list=[]

        if campaign.facebook_page_id and models.facebook.facebook_page.FacebookPage.objects.filter(id=campaign.facebook_page_id).exists():
            facebook_page = models.facebook.facebook_page.FacebookPage.objects.get(id=campaign.facebook_page_id)
            post_id=campaign.facebook_campaign.get('post_id')
            token=facebook_page.token   

            code, response = service.facebook.post.get_post_likes(token, post_id, after=None, limit=limit)
            if code!=200 :
                raise lib.error_handle.error.api_error.ApiVerifyError('Get Facebook Service Fail, Please Retry Again')
            likes_user_list += [user.get('name') for user in response.get('data',[])]

        campaign_comments = models.campaign.campaign_comment.CampaignComment.objects.filter(
            campaign=campaign,
            customer_name__in=likes_user_list
        )[:limit]

        for campaign_comment in campaign_comments:
        
            candidate = LuckyDrawCandidate(
                platform=campaign_comment.platform, 
                customer_id=campaign_comment.customer_id, 
                customer_name=campaign_comment.customer_name,
                customer_image=campaign_comment.image,
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

        order_products = models.order.order_product.OrderProduct.objects.filter(campaign=campaign, campaign_product=lucky_draw.campaign_product)

        for order_product in order_products:
            img_url = models.order.pre_order.PreOrder.objects.get(customer_id=order_product.customer_id, campaign=campaign.id).customer_img
            candidate = LuckyDrawCandidate(

                platform=order_product.platform, 
                customer_id=order_product.customer_id, 
                customer_name=order_product.customer_name,
                customer_image=img_url,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set


class PurchaseCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()

        orders = models.order.order.Order.objects.filter(campaign=campaign)
        pre_orders = models.order.pre_order.PreOrder.objects.filter(campaign=campaign,subtotal__gt=0)

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
        
        for pre_order in pre_orders:
            candidate = LuckyDrawCandidate(
                platform=pre_order.platform, 
                customer_id=pre_order.customer_id, 
                customer_name=pre_order.customer_name,
                customer_image=pre_order.customer_img,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set

class LuckyDraw():

    @classmethod
    def draw_from_candidate(cls, campaign, campaign_product, candidate_set=set(), num_of_winner=1):
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
                cls.__add_product(campaign, winner, campaign_product)
                cls.__announce(campaign, winner, campaign_product)
                cls.__send_private_message(campaign, winner, campaign_product)
                winner_dict = winner.to_dict()
                # if winner not in campaign_winner_list:
                campaign_winner_list.append(winner_dict)

                winner_list.append(winner_dict)
            except Exception:
                pass
            
        campaign.meta['winner_list']=campaign_winner_list
        campaign.save()

        return winner_list

    @classmethod
    def __add_product(
        cls, 
        campaign: models.campaign.campaign.Campaign, 
        winner:LuckyDrawCandidate, 
        campaign_product:models.campaign.campaign_product.CampaignProduct ):

            if models.order.pre_order.PreOrder.objects.filter(
                campaign=campaign, platform=winner.platform, customer_id=winner.customer_id, customer_name=winner.customer_name).exists():
                pre_order = models.order.pre_order.PreOrder.objects.get(
                    campaign=campaign, platform=winner.platform, customer_id=winner.customer_id, customer_name=winner.customer_name)
            else:
                platform_id_dict = {
                    'facebook': campaign.facebook_page.id if campaign.facebook_page else None,
                    'youtube': campaign.youtube_channel.id if campaign.youtube_channel else None,
                    'instagram': campaign.instagram_profile.id if campaign.instagram_profile else None
                }
                pre_order = models.order.pre_order.PreOrder.objects.create(
                    customer_id=winner.customer_id, 
                    customer_name=winner.customer_name, 
                    customer_img=winner.customer_image, 
                    campaign = campaign, 
                    platform=winner.platform, 
                    platform_id=platform_id_dict.get(winner.platform))


            if prize_product := pre_order.products.get(str(campaign_product.id), None):
                qty = prize_product['qty'] + 1
                lib.helper.order_helper.PreOrderHelper.update_product(api_user=None, pre_order_id=pre_order.id, 
                    order_product_id=prize_product.get('order_product_id'),qty=qty)
            else:
                lib.helper.order_helper.PreOrderHelper.add_product(api_user=None, pre_order_id=pre_order.id, campaign_product_id=campaign_product.id,qty=1)
            
    

    @classmethod
    def __announce(cls, 
    campaign: models.campaign.campaign.Campaign, 
    winner: LuckyDrawCandidate, 
    campaign_product:models.campaign.campaign_product.CampaignProduct):
        
        text = lib.i18n.campaign_announcement.get_campaign_announcement_lucky_draw_winner(campaign_product.name, winner.customer_name)


        if (facebook_page := campaign.facebook_page):
            service.facebook.post.post_page_comment_on_post(facebook_page.token, campaign.facebook_campaign.get('post_id'), text)
        

        if (youtube_channel := campaign.youtube_channel):
            service.youtube.live_chat.post_live_chat_comment(youtube_channel.token, campaign.youtube_campaign.get('live_chat_id'), text)

    @classmethod
    def __send_private_message(cls, 
    campaign: models.campaign.campaign.Campaign, 
    winner: LuckyDrawCandidate, 
    campaign_product:models.campaign.campaign_product.CampaignProduct):

        text = lib.i18n.campaign_announcement.get_campaign_announcement_lucky_draw_winner(campaign_product.name, winner.customer_name)  #temp

        if (campaign.instagram_profile and winner.platform=='instagram'):
            service.instagram.chat_bot.post_page_message_chat_bot(campaign.instagram_profile.connected_facebook_page_id, campaign.instagram_profile.token, winner.customer_id, text)


    
    @classmethod
    def __get_image(cls, winner:LuckyDrawCandidate):
        pass



def draw(campaign, lucky_draw):
    
    if lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_KEYWORD:
        candidate_set = lib.helper.lucky_draw_helper.KeywordCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
        return lib.helper.lucky_draw_helper.LuckyDraw.draw_from_candidate(campaign, lucky_draw.prize,  candidate_set=candidate_set, num_of_winner=lucky_draw.num_of_winner)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_LIKE:
        candidate_set = lib.helper.lucky_draw_helper.LikesCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
        return lib.helper.lucky_draw_helper.LuckyDraw.draw_from_candidate(campaign, lucky_draw.prize,  candidate_set=candidate_set, num_of_winner=lucky_draw.num_of_winner)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_PRODUCT:
        candidate_set = lib.helper.lucky_draw_helper.ProductCandidateSetGenerator.get_candidate_set(campaign, lucky_draw)
        return lib.helper.lucky_draw_helper.LuckyDraw.draw_from_candidate(campaign, lucky_draw.prize,  candidate_set=candidate_set, num_of_winner=lucky_draw.num_of_winner)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_PURCHASE:
        candidate_set = lib.helper.lucky_draw_helper.PurchaseCandidateSetGenerator.get_candidate_set(campaign, lucky_draw)
        return lib.helper.lucky_draw_helper.LuckyDraw.draw_from_candidate(campaign, lucky_draw.prize,  candidate_set=candidate_set, num_of_winner=lucky_draw.num_of_winner)
    else:
        return []

