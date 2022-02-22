from backend.api.facebook.post import api_fb_post_page_comment_on_post


class CampaignAnnouncementFacebookMessageAgent:
    @staticmethod
    def page_comment_on_post(page_token: str, post_id: str, message_text: str):
        return api_fb_post_page_comment_on_post(
            page_token, post_id, message_text)
