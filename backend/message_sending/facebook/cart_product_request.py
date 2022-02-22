from backend.api.facebook.post import (api_fb_post_page_comment_on_comment,
                                       api_fb_post_page_message_on_comment)


class CartProductRequestFacebookMessageAgent:
    @staticmethod
    def page_comment_on_comment(page_token: str, comment_id: str, message_text: str):
        return api_fb_post_page_comment_on_comment(
            page_token, comment_id, message_text)

    @staticmethod
    def page_message_on_comment(page_token: str, comment_id: str, message_text: str):
        return api_fb_post_page_message_on_comment(
            page_token, comment_id, message_text)
