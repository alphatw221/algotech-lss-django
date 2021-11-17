import pendulum
from api.models.campaign.campaign import Campaign


def get_active_campaign_now():
    return Campaign.objects.filter(
        start_at__lt=pendulum.now(),
        end_at__gt=pendulum.now(),
    )
