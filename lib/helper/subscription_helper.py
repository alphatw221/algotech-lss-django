def remove_pages(platform, user_subscription, id_of_binded_pages):
    if platform == "facebook":
        remove_pages = user_subscription.facebook_pages.exclude(page_id__in=id_of_binded_pages)
        for page in remove_pages:
            try:
                user_subscription.facebook_pages.remove(page)
                
            except:
                pass
            if not page.user_subscriptions.all().exists():
                page.delete()
    if platform == "instagram":
        remove_pages = user_subscription.instagram_profiles.exclude(business_id__in=id_of_binded_pages)
        for page in remove_pages:
            try:
                user_subscription.instagram_profiles.remove(page)
            except:
                pass
            if not page.user_subscriptions.all().exists():
                page.delete()
    if platform == "youtube":
        remove_pages = user_subscription.youtube_channels.exclude(channel_id__in=id_of_binded_pages)
        for page in remove_pages:
            try:
                user_subscription.youtube_channels.remove(page)
            except:
                pass
            if not page.user_subscriptions.all().exists():
                page.delete()