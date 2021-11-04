from django.contrib import admin

from api.models.test import sample
from api.models.user import user
from api.models.auto_response import auto_response
from api.models.campaign import campaign, campaign_product, campaign_order, campaign_comment, campaign_lucky_draw
from api.models.product import product
from api.models.order import order


admin.site.register(sample.Sample, sample.SampleAdmin)

admin.site.register(user.User, user.UserAdmin)

admin.site.register(auto_response.AutoResponse,
                    auto_response.AutoResponseAdmin)

admin.site.register(campaign.Campaign,
                    campaign.CampaignAdmin)
admin.site.register(campaign_product.CampaignProduct,
                    campaign_product.CampaignProductAdmin)
admin.site.register(campaign_order.CampaignOrder,
                    campaign_order.CampaignOrderAdmin)
admin.site.register(campaign_comment.CampaignComment,
                    campaign_comment.CampaignCommentAdmin)
admin.site.register(campaign_lucky_draw.CampaignLuckyDraw,
                    campaign_lucky_draw.CampaignLuckyDrawAdmin)

# admin.site.register(product.Product, product.ProductAdmin)

# admin.site.register(order.Order, order.OrderAdmin)
# admin.site.register(order_product.OrderProduct,
#                     order_product.OrderProductAdmin)
