from platform import platform
from typing import OrderedDict
from api import models
import service

import lib
import datetime
import numpy


class QuizGameCandidate():

    def __init__(self, platform, customer_id, customer_name="", customer_image="", prize=None, timestamp=[]):
        self.platform = platform
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_image = customer_image
        self.prize = prize
        self.timestamp = timestamp

    def __hash__(self) -> int:
        return (self.platform, self.customer_id).__hash__()

    def __eq__(self, __o: object) -> bool:
        try:
            if type(__o) in [dict, OrderedDict]:
                return self.platform == __o.get('platform') and self.customer_id == __o.get('customer_id')
            return self.platform == __o.platform and self.customer_id == __o.customer_id
        except Exception:
            return False

    def to_dict(self):
        return {'platform': self.platform, 'customer_id': self.customer_id, 'customer_name': self.customer_name, 'customer_image': self.customer_image, 'prize': self.prize, 'timestamp': self.timestamp}


class CandidateSetGenerator():

    @classmethod
    def get_candidate_set(cls):
        return set()


class QuizGameCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, quiz_game_bundle, limit=1000):
        winner_list = campaign.meta.get('winner_list', [])
        candidate_set = set()
        is_first_quiz = True

        cache = {}
        for quiz_game in quiz_game_bundle.quiz_games.all() :
            if not quiz_game.id or not quiz_game.start_at or not quiz_game.end_at:
                continue

            campaign_comments = campaign.comments.filter(
                message__icontains=quiz_game.answer,
                created_time__gte=datetime.datetime.timestamp(quiz_game.start_at),
                created_time__lte=datetime.datetime.timestamp(quiz_game.end_at)
            ).order_by('created_time')[:limit]

            alive_candidate_set = set()
            
            for campaign_comment in campaign_comments:
                if is_first_quiz == True:
                    candidate = QuizGameCandidate(
                        platform=campaign_comment.platform,
                        customer_id=campaign_comment.customer_id,
                        customer_name=campaign_comment.customer_name,
                        customer_image=campaign_comment.image,
                        prize=quiz_game_bundle.prize.name,
                        timestamp=campaign_comment.created_time
                    )
                    if not quiz_game_bundle.repeatable and candidate in winner_list:
                        continue
                    if candidate not in candidate_set:
                        cache[f'{campaign_comment.platform}{campaign_comment.customer_id}'] = campaign_comment.created_time
                        candidate_set.add(candidate)
                else:
                    candidate = QuizGameCandidate(
                        platform=campaign_comment.platform,
                        customer_id=campaign_comment.customer_id,
                        customer_name=campaign_comment.customer_name,
                        customer_image=campaign_comment.image,
                        prize=quiz_game_bundle.prize.name,
                        timestamp= campaign_comment.created_time
                    )
                    if candidate in candidate_set and candidate not in alive_candidate_set:
                        cache[f'{campaign_comment.platform}{campaign_comment.customer_id}'] += campaign_comment.created_time
                        candidate.timestamp = cache[f'{campaign_comment.platform}{campaign_comment.customer_id}']
                        alive_candidate_set.add(candidate)

            if not is_first_quiz: 
                candidate_set = alive_candidate_set.copy()
            is_first_quiz = False
        
        return candidate_set
    

class QuizGame():

    @classmethod
    def get_winner_from_candidate(cls, campaign, quiz_game_bundle, candidate_set=set()):

        if not candidate_set:
            return []

        num_of_winner = len(candidate_set) if quiz_game_bundle.num_of_winner > len(candidate_set) else quiz_game_bundle.num_of_winner

        timestamp_list = []
        candidate_list = []
        for candidate in candidate_set:
            timestamp_list.append(candidate.timestamp)
            candidate_list.append(candidate)

        rank_indexs = numpy.array(timestamp_list).argsort()

        np_candidate_list = numpy.array(candidate_list)

        winners = list(np_candidate_list[rank_indexs[:num_of_winner]])
        if not winners:
            return []
        
        campaign_winner_list = campaign.meta.get('winner_list',[])
        winner_list = []
        for winner in winners:                                              #multithread needed
            cls.__add_product(campaign, winner, quiz_game_bundle.prize)
            cls.__announce(campaign, winner, quiz_game_bundle.prize)
            cls.__send_private_message(campaign, winner, quiz_game_bundle.prize)
            winner_dict = winner.to_dict()

            campaign_winner_list.append(winner_dict)
            winner_list.append(winner_dict)

        quiz_game_bundle.winner_list = winner_list
        quiz_game_bundle.save()
        campaign.meta['winner_list']=campaign_winner_list
        campaign.save()

        return winner_list
    
    
    @classmethod
    def __add_product(
        cls, 
        campaign: models.campaign.campaign.Campaign, 
        winner: QuizGameCandidate, 
        campaign_product: models.campaign.campaign_product.CampaignProduct ):

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
    winner: QuizGameCandidate, 
    campaign_product: models.campaign.campaign_product.CampaignProduct):
        
        text = lib.i18n.campaign_announcement.get_campaign_announcement_quiz_game_winner(campaign_product.name, winner.customer_name, lang=campaign.lang)

        if (facebook_page := campaign.facebook_page):
            service.facebook.post.post_page_comment_on_post(facebook_page.token, campaign.facebook_campaign.get('post_id'), text)
        if (youtube_channel := campaign.youtube_channel):
            service.youtube.live_chat.post_live_chat_comment(youtube_channel.token, campaign.youtube_campaign.get('live_chat_id'), text)

    @classmethod
    def __send_private_message(cls, 
    campaign: models.campaign.campaign.Campaign, 
    winner: QuizGameCandidate, 
    campaign_product: models.campaign.campaign_product.CampaignProduct):

        text = lib.i18n.campaign_announcement.get_campaign_announcement_quiz_game_winner(campaign_product.name, winner.customer_name, lang=campaign.lang)  #temp

        if (campaign.instagram_profile and winner.platform=='instagram'):
            service.instagram.chat_bot.post_page_message_chat_bot(campaign.instagram_profile.connected_facebook_page_id, campaign.instagram_profile.token, winner.customer_id, text)


def quiz(campaign, quiz_game_bundle):
    candidate_set = lib.helper.quiz_game_helper.QuizGameCandidateSetGenerator.get_candidate_set(campaign, quiz_game_bundle, limit=100)
    return lib.helper.quiz_game_helper.QuizGame.get_winner_from_candidate(campaign, quiz_game_bundle, candidate_set=candidate_set)
