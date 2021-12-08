from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from api.models.campaign.campaign_comment import CampaignComment
from api.models.facebook.facebook_page import FacebookPage
from api.models.instagram.instagram_profile import InstagramProfile
from api.models.youtube.youtube_channel import YoutubeChannel
from backend.i18n.comment_command import i18n_get_comment_command_response
from backend.message_sending.facebook.cart_product_request import \
    CartProductRequestFacebookMessageAgent as FacebookMessageAgent
from backend.utils.text_processing.command_processor import Command


@dataclass
class CampaginCommentResponder(ABC):
    @abstractmethod
    def process():
        ...


@dataclass
class PlatformCampaginCommentResponder(ABC):
    @abstractmethod
    def process():
        ...


@dataclass
class CampaginCommentResponderCommand(CampaginCommentResponder):
    response_platforms: dict = field(default_factory=dict)

    def process(self, comment: CampaignComment, command: Command,
                responder: PlatformCampaginCommentResponder = None):
        if platform_object := self._get_platform_object(comment):
            if not responder:
                if isinstance(platform_object, FacebookPage):
                    responder = FacebookCommentPrivateMessageResponder(
                        command, comment, platform_object)
                elif isinstance(platform_object, YoutubeChannel):
                    ...  # TODO implement YoutubeChannel
                elif isinstance(platform_object, InstagramProfile):
                    ...  # TODO implement InstagramProfile

            if responder:
                return responder.process

    def _get_platform_object(self, comment: CampaignComment):
        if (platform := comment.platform) in self.response_platforms:
            return self.response_platforms[platform]
        return None


@dataclass
class FacebookCommentPrivateMessageResponder(PlatformCampaginCommentResponder):
    command: Command
    comment: CampaignComment
    facebook_page: FacebookPage
    response_result: dict = field(default_factory=dict)

    def __post_init__(self):
        self.token = self.facebook_page.token

    def process(self):
        if self.token:
            text = i18n_get_comment_command_response(
                self.comment, self.command, lang=self.facebook_page.lang)

            self.response_result['text'] = text

            self.response_result['private_message'] = FacebookMessageAgent.page_message_on_comment(
                self.token, self.comment.comment_id, text)

        self.comment.meta['response_result'] = self.response_result
        self.comment.save()
