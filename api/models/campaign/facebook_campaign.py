from dataclasses import dataclass


@dataclass
class FacebookCampaign:
    post_id: str = ''
    live_video_id: str = ''
    embed_url: str = ''
    remark: str = ''
