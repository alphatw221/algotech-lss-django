from django.contrib import admin

from api.models.auto_response import auto_response
from api.models.campaign import (campaign, campaign_comment,
                                 campaign_lucky_draw, campaign_product)
from api.models.cart import cart_product
from api.models.order import order
from api.models.product import product
from api.models.test import sample
from api.models.user import user, user_group, user_plan

admin.site.register(sample.Sample, sample.SampleAdmin)

admin.site.register(user.User, user.UserAdmin)
admin.site.register(user_group.UserGroup, user_group.UserGroupAdmin)
admin.site.register(user_plan.UserPlan, user_plan.UserPlanAdmin)

admin.site.register(auto_response.AutoResponse,
                    auto_response.AutoResponseAdmin)

admin.site.register(campaign.Campaign,
                    campaign.CampaignAdmin)
admin.site.register(campaign_product.CampaignProduct,
                    campaign_product.CampaignProductAdmin)

admin.site.register(campaign_comment.CampaignComment,
                    campaign_comment.CampaignCommentAdmin)
admin.site.register(campaign_lucky_draw.CampaignLuckyDraw,
                    campaign_lucky_draw.CampaignLuckyDrawAdmin)

admin.site.register(product.Product, product.ProductAdmin)

admin.site.register(cart_product.CartProduct,
                    cart_product.CartProductAdmin)

# admin.site.register(order.Order, order.OrderAdmin)
