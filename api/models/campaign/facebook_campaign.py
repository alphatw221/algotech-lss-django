from dataclasses import dataclass


@dataclass
class FacebookCampaign:
    page_id: str = ''
    post_id: str = ''
    live_video_id: str = ''
    embed_url: str = ''
