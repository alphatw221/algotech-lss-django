import pendulum
from api.models.campaign.campaign import Campaign


def get_active_campaign_now():
    try:
        return Campaign.objects.filter(
            start_at__lt=pendulum.now(),
            end_at__gt=pendulum.now(),
        )
    except Exception:
        return []


def get_ordering_campaign_now():
    try:
        return Campaign.objects.filter(
            start_at__lt=pendulum.now(),
            end_at__gt=pendulum.now(),
        )
    except Exception:
        return []
