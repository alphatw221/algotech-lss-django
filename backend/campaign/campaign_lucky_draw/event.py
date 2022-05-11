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
                # winner_datas, img_url = db.api_pre_order.find({'customer_id': order_data['customer_id'], 'campaign_id': self.campaign.id}), ''
                # for winner_data in winner_datas:
                #     img_url = winner_data['customer_img']
                candidate_set.add(
                    (order_data['platform'], order_data['customer_id'], order_data['customer_name'])
                )
        for order_data in pre_order_datas:
            if order_data['customer_id'] == page_id:
                continue
            else:
                # winner_datas, img_url = db.api_pre_order.find({'customer_id': order_data['customer_id'], 'campaign_id': self.campaign.id}), ''
                # for winner_data in winner_datas:
                #     img_url = winner_data['customer_img']
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
            if order_product.customer_id == page_id:
                continue
            else:
                # winner_datas, img_url = db.api_pre_order.find({'customer_id': order_product.customer_id, 'campaign_id': self.campaign.id}), ''
                # for winner_data in winner_datas:
                #     img_url = winner_data['customer_img']
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

        winner_set = set()
        if self.unrepeat == 'True':
            winner_set = get_winner_set(self.campaign.id)
        
        page_id = ''
        if self.campaign.facebook_page_id:
            page_id = db.api_facebook_page.find_one({'id': self.campaign.facebook_page_id})['page_id']

        candidate_set = set()
        for campaign_comment in campaign_comments:
            if (campaign_comment['customer_id'] == page_id):
                continue
            else:
                #TODO 回傳label到candidate set建完後 再依照label取img
                # winner_datas, img_url = db.api_campaign_comment.find({'customer_id': campaign_comment['customer_id'], 'campaign_id': self.campaign.id}), ''
                # for winner_data in winner_datas:
                #     img_url = winner_data['image']
                candidate_set.add(
                    (campaign_comment['platform'], campaign_comment['customer_id'], campaign_comment['customer_name'])
                )
        
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
                        #TODO 回傳label到candidate set建完後 再依照label取img
                        # winner_datas, img_url = db.api_user.find({'facebook_info.id': person['id'], 'type': 'customer'}), ''
                        # for winner_data in winner_datas:
                        #     img_url = winner_data['facebook_info']['picture']
                        candidate_set.add(
                            ('facebook', person['id'], person['name'], person['pic_large'])
                        )
                try:
                    after = response[1]['paging']['cursors']['after']
                except Exception:
                    break
            #TODO remove campaign itself
        if self.unrepeat == 'True':
            candidate_set = get_final_set(candidate_set, winner_set, self.winner_num)
        
        return candidate_set


#TODO 造成一個meta 每次都從meta抓取 不要重run整個db query
def get_winner_set(campaign_id):
    winner_set = set()
    meta = db.api_campaign.find_one({'id': campaign_id})['meta']
    winner_list = meta.get('winner_list', [])
    if winner_list:
        for winner in winner_list:
            winner_set.add(winner[1])

    return winner_set


def get_final_set(candidate_set, winner_set, winner_num):
    exclusive_set = set()
    for candidate in candidate_set:
        if candidate[1] in winner_set:
            continue
        else:
            exclusive_set.add(candidate) 
    if len(exclusive_set) < winner_num:
        exclusive_set = candidate_set
    candidate_set = exclusive_set

    return candidate_set
    
