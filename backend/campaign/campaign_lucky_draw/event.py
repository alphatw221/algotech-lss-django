from abc import ABC, abstractmethod
from dataclasses import dataclass

from django.db.models.fields import BooleanField
from api.models import campaign

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.order import order_product
from api.models.order.order_product import OrderProduct
from api.utils.orm import campaign_comment as orm_campaign_comment
from api.utils.orm import cart_product as orm_cart_product

from backend.api.facebook.post import api_fb_get_post_likes
from backend.pymongo.mongodb import db, client


@dataclass
class CampaignLuckyDrawEvent(ABC):
    @abstractmethod
    def get_source_id(self):
        ...

    @abstractmethod
    def get_source_type(self):
        ...

    @abstractmethod
    def get_condition(self):
        ...

    @abstractmethod
    def get_condition_type(self):
        ...

    @abstractmethod
    def get_candidate_set(self):
        ...


@dataclass
class DrawFromProductsEvent(CampaignLuckyDrawEvent):
    campaign: Campaign
    campaign_product: CampaignProduct
    unrepeat: str
    winner_num: int

    def get_source_id(self):
        return self.campaign_product.id

    def get_source_type(self):
        return 'campaign_product'

    def get_condition(self):
        return None

    def get_condition_type(self):
        return 'lucky_draw_products'

    def get_candidate_set(self):
        # cart_products = orm_cart_product.filter_products(
        #     self.campaign,
        #     ('order_code', 'cart'),
        #     ('valid',)
        # )
        order_datas = db.api_order.find({'campaign_id': self.campaign.id})
        pre_order_datas = db.api_pre_order.find({'campaign_id': self.campaign.id})

        winner_set = set()
        if self.unrepeat == 'True':
            winner_set = get_winner_set(self.campaign.id)
        
        page_id = ''
        if self.campaign.facebook_page_id:
            page_id = db.api_facebook_page.find_one({'id': self.campaign.facebook_page_id})['page_id']

        candidate_set = set()
        for order_data in order_datas:
            if order_data['customer_id'] == page_id:
                continue
            else:
                candidate_set.add(
                    (order_data['platform'], order_data['customer_id'], order_data['customer_name'])
                )
        for order_data in pre_order_datas:
            if order_data['customer_id'] == page_id:
                continue
            else:
                candidate_set.add(
                    (order_data['platform'], order_data['customer_id'], order_data['customer_name'])
                )
        if self.unrepeat == 'True':
            candidate_set = get_final_set(candidate_set, winner_set, self.winner_num)
        
        return candidate_set


@dataclass
class DrawFromCartProductsEvent(CampaignLuckyDrawEvent):
    campaign: Campaign
    campaign_product: CampaignProduct
    unrepeat: str
    winner_num: int

    def get_source_id(self):
        return self.campaign_product.id

    def get_source_type(self):
        return 'campaign_product'

    def get_condition(self):
        return None

    def get_condition_type(self):
        return 'lucky_draw_cart_products'

    def get_candidate_set(self):
        order_products = OrderProduct.objects.filter(campaign=self.campaign, campaign_product=self.campaign_product)
        winner_set = set()
        if self.unrepeat == 'True':
            winner_set = get_winner_set(self.campaign.id)
        
        page_id = ''
        if self.campaign.facebook_page_id:
            page_id = db.api_facebook_page.find_one({'id': self.campaign.facebook_page_id})['page_id']
        
        candidate_set = set()
        for order_product in order_products:
            print ('order_product')
            print (order_product)
            if order_product.customer_id == page_id:
                continue
            else:
                candidate_set.add(
                    (order_product.platform, order_product.customer_id, order_product.customer_name)
                )
        
        if self.unrepeat == 'True':
            candidate_set = get_final_set(candidate_set, winner_set, self.winner_num)
            
        return candidate_set


@dataclass
class DrawFromCampaignCommentsEvent(ABC):
    campaign: Campaign
    keyword: str
    unrepeat: str
    winner_num: int

    def get_source_id(self):
        return self.campaign.id

    def get_source_type(self):
        return 'campaign'

    def get_condition(self):
        return self.keyword

    def get_condition_type(self):
        return 'lucky_draw_campaign_comments'

    def get_candidate_set(self):
        campaign_comments = orm_campaign_comment.get_keyword_campaign_comments(
            self.campaign, self.keyword,
        )
        # campaign_comments = db.api_campaign_comment.find({'campaign_id': self.campaign.id, 'message': {'$regex': '.*[' + self.keyword + '].*'}})
        
        winner_set = set()
        if self.unrepeat == 'True':
            winner_set = get_winner_set(self.campaign.id)
        
        page_id = ''
        if self.campaign.facebook_page_id:
            page_id = db.api_facebook_page.find_one({'id': self.campaign.facebook_page_id})['page_id']

        candidate_set = set()
        for campaign_comment in campaign_comments:
            print ('campaign_comment')
            print (campaign_comment)
            if (campaign_comment['customer_id'] == page_id):
                continue
            else:
                candidate_set.add(
                    (campaign_comment['platform'], campaign_comment['customer_id'], campaign_comment['customer_name'])
                )
        print ('candidate_set')
        print (candidate_set)
        
        if self.unrepeat == 'True':
            candidate_set = get_final_set(candidate_set, winner_set, self.winner_num)

        return candidate_set


@dataclass
class DrawFromCampaignLikesEvent(ABC):
    campaign: Campaign
    unrepeat: str
    winner_num: int

    def get_source_id(self):
        return self.campaign.id

    def get_source_type(self):
        return 'campaign'

    def get_condition(self):
        return None

    def get_condition_type(self):
        return 'lucky_draw_campaign_likes'

    def get_candidate_set(self):
        candidate_set = set()

        winner_set = set()
        if self.unrepeat == 'True':
            winner_set = get_winner_set(self.campaign.id)

        if self.campaign.facebook_campaign and (post_id := self.campaign.facebook_campaign.get('post_id')) and \
                self.campaign.facebook_page and (token := self.campaign.facebook_page.token):
            after = None

            page_id = ''
            # remove facebook campaign itself
            if self.campaign.facebook_page_id:
                page_id = db.api_facebook_page.find_one({'id': self.campaign.facebook_page_id})['page_id']
            
            while True:
                response = api_fb_get_post_likes(token, post_id, after=after)
                for person in response[1]['data']:
                    if (person['id'] == page_id):
                        continue
                    else:
                        candidate_set.add(
                            ('facebook', person['id'], person['name'])
                        )
                try:
                    after = response[1]['paging']['cursors']['after']
                except Exception:
                    break

            #TODO remove campaign itself
        if self.unrepeat == 'True':
            candidate_set = get_final_set(candidate_set, winner_set, self.winner_num)
        
        return candidate_set


def get_winner_set(campaign_id):
    winner_set = set()
    lucky_winners = db.api_campaign_lucky_draw.find({'campaign_id': campaign_id})
    for lucky_winner in lucky_winners:
        try:
            for winner in lucky_winner['winner_list']:
                winner_set.add(winner[1])
        except:
            continue
    return winner_set


def get_final_set(candidate_set, winner_set, winner_num):
    exclusive_set = set()
    for candidate in candidate_set:
        if not candidate[1] in winner_set:
            exclusive_set.add(candidate) 
    print ('exclusive_set')
    print (exclusive_set)
    if (len(exclusive_set) <= winner_num):
        exclusive_set = candidate_set
    candidate_set = exclusive_set

    return candidate_set
    
