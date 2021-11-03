from django.contrib import admin

from .models import (
    sample,
    user,
    auto_response,
    campaign,
    campaign_product,
    campaign_order,
    order_product,
    campaign_lucky_draw,
    campaign_comment,
    product,
    order
)


admin.site.register(sample.Sample, sample.SampleAdmin)

admin.site.register(user.User, user.UserAdmin)

admin.site.register(auto_response.AutoResponse,
                    auto_response.AutoResponseAdmin)
admin.site.register(product.Product, product.ProductAdmin)

admin.site.register(order_product.OrderProduct,
                    order_product.OrderProductAdmin)
admin.site.register(order.Order, order.OrderAdmin)

admin.site.register(campaign.Campaign, campaign.CampaignAdmin)
admin.site.register(campaign_product.CampaignProduct,
                    campaign_product.CampaignProductAdmin)
admin.site.register(campaign_order.CampaignOrder,
                    campaign_order.CampaignOrderAdmin)
admin.site.register(campaign_lucky_draw.CampaignLuckyDraw,
                    campaign_lucky_draw.CampaignLuckyDrawAdmin)
admin.site.register(campaign_comment.CampaignComment,
                    campaign_comment.CampaignCommentAdmin)
