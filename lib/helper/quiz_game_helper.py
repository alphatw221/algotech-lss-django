from typing import OrderedDict
from api import models

import lib
import datetime


class QuizGameCandidate():

    def __init__(self, platform, customer_id, customer_name="", customer_image="", prize=None):
        self.platform = platform
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_image = customer_image
        self.prize = prize

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
        return {'platform': self.platform, 'customer_id': self.customer_id, 'customer_name': self.customer_name, 'customer_image': self.customer_image, 'prize': self.prize}


class CandidateSetGenerator():

    @classmethod
    def get_candidate_set(cls):
        return set()


class QuizGameCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, quiz_game, limit=1000):
        #TODO combine quiz_game winner list
        winner_list = campaign.meta.get('winner_list', [])

        print (winner_list)
        print ('--------------')
        [winner_dict.pop('draw_type', None) for winner_dict in winner_list]


        candidate_set = set()
        campaign_comments = models.campaign.campaign_comment.CampaignComment.objects.filter(
            campaign=campaign,
            message__icontains=quiz_game.answer,
            created_time__gte=datetime.datetime.timestamp(quiz_game.start_at),
            created_time__lte=datetime.datetime.timestamp(quiz_game.end_at)
        ).order_by('created_time')[:limit]

        for campaign_comment in campaign_comments:
            candidate = QuizGameCandidate(
                platform=campaign_comment.platform,
                customer_id=campaign_comment.customer_id,
                customer_name=campaign_comment.customer_name,
                customer_image=campaign_comment.image,
                prize=quiz_game.prize.name)

            if not quiz_game.repeatable and candidate in winner_list:
                continue
            candidate_set.add(candidate)

        return candidate_set
    
    

class QuizGame():

    @classmethod
    def get_winner_from_candidate(cls, campaign, campaign_product, candidate_set=set(), num_of_winner=1):
        if not candidate_set:
            print('no candidate')
            return []
        num_of_winner = len(candidate_set) if num_of_winner > len(candidate_set) else num_of_winner

        winners = list(candidate_set)[0:num_of_winner]
        if not winners:
            print('no winners')
            return []
        
        #TODO combine with quiz winner list
        campaign_winner_list = campaign.meta.get('winner_list',[])
        winner_list = []
        
        for winner in winners:                                              #multithread needed
            try:
                # cls.__add_product(campaign, winner, campaign_product)
                # cls.__announce(campaign, winner, campaign_product)
                # cls.__send_private_message(campaign, winner, campaign_product)
                winner_dict = winner.to_dict()
                # if winner not in campaign_winner_list:
                campaign_winner_list.append(winner_dict)

                winner_list.append(winner_dict)
            except Exception:
                pass
        
        # print ('---------------------------------------------')
        # print (winner_list)
        # campaign.meta['winner_list']=campaign_winner_list
        # campaign.save()

        return winner_list


def quiz(campaign, quiz_game):
    candidate_set = lib.helper.quiz_game_helper.QuizGameCandidateSetGenerator.get_candidate_set(campaign, quiz_game, limit=100)
    
    return lib.helper.quiz_game_helper.QuizGame.get_winner_from_candidate(campaign, quiz_game.prize,  candidate_set=candidate_set, num_of_winner=quiz_game.num_of_winner)
