from api.models.campaign.campaign_comment import CampaignComment
from backend.campaign.campaign_comment.command_responder import \
    CampaginCommentResponder
from backend.utils.text_processing._text_processor import TextProcessor


class CommentPluginCommand():
    @staticmethod
    def process(text_processor: TextProcessor,
                comment: CampaignComment,
                batch_tasks_list: list,
                ccr: CampaginCommentResponder):
        command = text_processor.process(comment.message)
        if not command:
            return None

        comment.meta['CommentPluginCommand'] = f'{command!r}'

        if task := ccr.process(comment, command):
            batch_tasks_list.append(task)
            return True
