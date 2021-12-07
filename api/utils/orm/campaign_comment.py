from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from django.db.models import Count


def get_latest_commented_at(campaign: Campaign, platform: str):
    try:
        return CampaignComment.objects.filter(
            campaign=campaign,
            platform=platform
        ).latest('commented_at').commented_at
    except Exception:
        return 1


def update_or_create_comment(campaign: Campaign, platform: str,
                             comment_id: str, defaults: dict):
    try:
        CampaignComment.objects.update_or_create(
            campaign=campaign,
            platform=platform,
            comment_id=comment_id,
            defaults=defaults)
    except Exception:
        ...


def get_comments_count(campaign: Campaign, platform: str):
    try:
        return CampaignComment.objects.filter(
            campaign=campaign,
            platform=platform
        ).count()
    except Exception:
        return 0


def get_campaign_comments(campaign: Campaign, status: int = None,
                          order_by: str = 'pk', limit: int = 1000):
    try:
        campaign_comments = CampaignComment.objects.filter(campaign=campaign)
        if status is not None:
            campaign_comments = campaign_comments.filter(status=status)

        return campaign_comments.order_by(order_by).all()[:limit]
    except Exception:
        return []


def get_keyword_campaign_comments(campaign: Campaign, keyword: str,
                                  limit: int = 1000):
    try:
        return CampaignComment.objects.filter(
            campaign=campaign,
            message__contains=keyword,
        ).values('customer_id', 'customer_name', 'platform').annotate(count=Count('customer_id')).order_by('pk')[:limit]
    except Exception:
        return []
