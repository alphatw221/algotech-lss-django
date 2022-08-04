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
        ## TODO combine quiz_game winner list to lucky draw
        winner_list = campaign.meta.get('winner_list', [])
        campaign_quiz_game_bundles = models.campaign.campaign_quiz_game_bundle.CampaignQuizGameBundle.objects.filter(campaign=campaign)
        for campaign_quiz_game_bundle in campaign_quiz_game_bundles:
            winner_list += list(campaign_quiz_game_bundle.winner_list)

        candidate_set = set()
        candidate_list = []
        quizgameid_list = []
        go_comparing = False

        quiz_games = models.campaign.campaign_quiz_game.CampaignQuizGameBundleSerializerWithEachQuiz(quiz_game_bundle).data.get('quiz_games')
        for quiz_game in quiz_games:
            quiz_id, quiz_game_start_at, quiz_game_end_at = 0, '', ''
            for key, val in quiz_game.items():
                if key == 'id': quiz_id = val
                if key == 'start_at': quiz_game_start_at = val 
                if key == 'end_at': quiz_game_end_at = val 
          
            if quiz_id != 0 and quiz_game_start_at not in [None, ''] and quiz_game_end_at not in [None, '']:
                quizgame = models.campaign.campaign_quiz_game.CampaignQuizGame.objects.get(id=quiz_id)
                quizgameid_list.append(quizgame.id)
                campaign_comments = models.campaign.campaign_comment.CampaignComment.objects.filter(
                    campaign=campaign,
                    message__icontains=quizgame.answer,
                    created_time__gte=datetime.datetime.timestamp(quizgame.start_at),
                    created_time__lte=datetime.datetime.timestamp(quizgame.end_at)
                ).order_by('created_time')[:limit]

                for campaign_comment in campaign_comments:
                    if go_comparing == False:
                        candidate_dict = {
                            'platform': campaign_comment.platform,
                            'customer_id': campaign_comment.customer_id,
                            'customer_name': campaign_comment.customer_name,
                            'customer_image': campaign_comment.image,
                            'prize': quiz_game_bundle.prize.name,
                            'created_time': [{ quizgame.id : campaign_comment.created_time }]
                        }
                        candidate_list.append(candidate_dict)
                    else:
                        for candidate_dict in candidate_list:
                            ## find exists quiz_game_id to compare created_time later
                            created_time_list = candidate_dict.get('created_time', [])
                            exist_quizgame_id_list = []
                            for created_time in created_time_list:
                                exist_quizgame_id_list.append(list(created_time.keys())[0])

                            if candidate_dict.get('platform', '') == campaign_comment.platform and candidate_dict.get('customer_id', '') == campaign_comment.customer_id:
                                if quizgame.id in exist_quizgame_id_list:
                                    for created_time in created_time_list:
                                        if quizgame.id == list(created_time.keys())[0] and campaign_comment.created_time < created_time[quizgame.id]:
                                            created_time[quizgame.id] = campaign_comment.created_time
                                else:
                                    created_time_list.append({ quizgame.id : campaign_comment.created_time })
            go_comparing = True

        ## filter out not answer all question candidate
        for i in range(len(candidate_list)):
            candidate_quizgame_id_list = []
            for created_time in candidate_list[i].get('created_time', []):
                [candidate_quizgame_id_list.append(key) for key in created_time.keys()]
            if quizgameid_list != candidate_quizgame_id_list:
                del candidate_list[i]
        
        for candidate_dict in candidate_list:
            total_timestamp = 0
            created_time_list = candidate_dict.get('created_time')
            for created_time in created_time_list:
                for quizgame_id, created_at in created_time.items():
                    total_timestamp += created_at

            candidate = QuizGameCandidate(
                platform=candidate_dict.get('platform', ''),
                customer_id=candidate_dict.get('customer_id', ''),
                customer_name=candidate_dict.get('customer_name', ''),
                customer_image=candidate_dict.get('image', ''),
                prize=quiz_game_bundle.prize.name,
                timestamp=total_timestamp
            )

            ## TODO repeatable winner checker
            # if not quiz_game.repeatable and candidate in winner_list:
            #     continue
            candidate_set.add(candidate)

        return candidate_set
    
    

class QuizGame():

    @classmethod
    def get_winner_from_candidate(cls, campaign, quiz_game_bundle, candidate_set=set()):
        if not candidate_set:
            print('no candidate')
            return []
        num_of_winner = len(candidate_set) if quiz_game_bundle.num_of_winner > len(candidate_set) else quiz_game_bundle.num_of_winner

        timestamp_list = []
        for candidate in list(candidate_set):
            timestamp_list.append(candidate.to_dict().get('timestamp', 9999999999))

        ranking_dict = {}
        array = numpy.array(timestamp_list)
        temp = array.argsort()
        ranks = numpy.empty_like(temp)
        ranks[temp] = numpy.arange(len(array))
        ranking_list = [i + 1 for i in list(ranks)]
        ranking_dict = dict(zip(timestamp_list, ranking_list))

        for timestamp, ranking in ranking_dict.items():
            if ranking > num_of_winner:
                for candidate in list(candidate_set):
                    if timestamp == candidate.to_dict().get('timestamp', 9999999999):
                        candidate_set.remove(candidate)
        
        winners = list(candidate_set)
        if not winners:
            print('no winners')
            return []
        
        winner_list = []
        for winner in winners:                                              #multithread needed
            cls.__add_product(campaign, winner, quiz_game_bundle.prize)
            cls.__announce(campaign, winner, quiz_game_bundle.prize)
            cls.__send_private_message(campaign, winner, quiz_game_bundle.prize)
            winner_dict = winner.to_dict()
            winner_list.append(winner_dict)

        quiz_game_bundle.winner_list = winner_list
        quiz_game_bundle.save()

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
        
        text = lib.i18n.campaign_announcement.get_campaign_announcement_quiz_game_winner(campaign_product.name, winner.customer_name)

        if (facebook_page := campaign.facebook_page):
            service.facebook.post.post_page_comment_on_post(facebook_page.token, campaign.facebook_campaign.get('post_id'), text)
        if (youtube_channel := campaign.youtube_channel):
            service.youtube.live_chat.post_live_chat_comment(youtube_channel.token, campaign.youtube_campaign.get('live_chat_id'), text)

    @classmethod
    def __send_private_message(cls, 
    campaign: models.campaign.campaign.Campaign, 
    winner: QuizGameCandidate, 
    campaign_product: models.campaign.campaign_product.CampaignProduct):

        text = lib.i18n.campaign_announcement.get_campaign_announcement_quiz_game_winner(campaign_product.name, winner.customer_name)  #temp

        if (campaign.instagram_profile and winner.platform=='instagram'):
            service.instagram.chat_bot.post_page_message_chat_bot(campaign.instagram_profile.connected_facebook_page_id, campaign.instagram_profile.token, winner.customer_id, text)


def quiz(campaign, quiz_game_bundle):
    candidate_set = lib.helper.quiz_game_helper.QuizGameCandidateSetGenerator.get_candidate_set(campaign, quiz_game_bundle, limit=100)
    return lib.helper.quiz_game_helper.QuizGame.get_winner_from_candidate(campaign, quiz_game_bundle, candidate_set=candidate_set)
