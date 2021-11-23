from enum import Enum, auto

from backend.i18n._helper import lang_kwarg_translate
from django.utils.translation import ugettext as _


class CampaignAnnouncement(Enum):
    CAMPAIGN_PRODUCT_CLOSED = auto()
    CAMPAIGN_PRODUCT_SOLD_OUT = auto()
    LUCKY_DRAW_WINNER = auto()


@lang_kwarg_translate
def i18n_get_campaign_announcement(type: CampaignAnnouncement, lang=None):
    ...
