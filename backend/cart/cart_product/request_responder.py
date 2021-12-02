from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from backend.cart.cart_product.request import CartProductRequest
from backend.i18n.cart_product_request import (i18n_get_additional_text,
                                               i18n_get_request_response)
from backend.message_sending.facebook.cart_product_request import \
    CartProductRequestFacebookMessageAgent as FacebookMessageAgent


class CartProductRequestResponder(ABC):
    def process():
        ...


@dataclass
class AbstractCartProductRequestResponder(ABC):
    @abstractmethod
    def process():
        ...


@dataclass
class CartProductRequestResponderOrderCode(CartProductRequestResponder):
    response_platforms: dict = field(default_factory=dict)

    def process(self, request: CartProductRequest,
                responder: AbstractCartProductRequestResponder = None):
        if platform_object := self._get_platform_object(request):
            if not responder:
                if isinstance(platform_object, FacebookPage):
                    responder = FacebookCommentCommentPrivateMessageResponder(
                        request, platform_object)
                elif isinstance(platform_object, YoutubeChannel):
                    ...

            if responder:
                request.response_task = responder.process

    def _get_platform_object(self, request: CartProductRequest):
        if (platform := request.platform) in self.response_platforms:
            return self.response_platforms[platform]
        return None


@dataclass
class FacebookCommentCommentPrivateMessageResponder(AbstractCartProductRequestResponder):
    request: CartProductRequest
    facebook_page: FacebookPage
    response_result: dict = field(default_factory=dict)

    def __post_init__(self):
        self.token = self.facebook_page.token
        self.comment = self.request.campaign_comment

    def process(self):
        if self.token:
            text = i18n_get_request_response(
                self.request, lang=self.facebook_page.lang)
            shopping_cart_info, info_in_pm_notice = i18n_get_additional_text(
                lang=self.facebook_page.lang)
            self.response_result['text'] = text

            self.response_result['comment'] = FacebookMessageAgent.page_comment_on_comment(
                self.token, self.comment.comment_id, text + info_in_pm_notice)

            self.response_result['private_message'] = FacebookMessageAgent.page_message_on_comment(
                self.token, self.comment.comment_id, text + shopping_cart_info)

        self.comment.meta['response_result'] = self.response_result
        self.comment.save()
