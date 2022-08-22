from django.conf import settings
from api import models
import service
import lib

from datetime import datetime

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
                status_code, response = service.facebook.page.delete_page_webhook(page.token, page.page_id)
                if status_code == 200:
                    print(page, "delete webhook setting")
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


def bind_facebook_pages(request, user_subscription):
    token, = lib.util.getter.getdata(request,('accessToken',), required=True)
    status_code, response = service.facebook.user.get_me_accounts(token)
    print(status_code)
    print(response)
    if status_code != 200:
        raise lib.error_handle.error.api_error.ApiCallerError("helper.api_fb_get_accounts_error")


    for item in response.get('data',[]):
        page_token = item.get('access_token')
        page_id = item.get('id')
        page_name = item.get('name')
        status_code, picture_data = service.facebook.page.get_page_picture(page_token=page_token, page_id=page_id, height=100, width=100)


        
        page_image = item['image'] = picture_data.get('data',{}).get('url') if status_code == 200 else None
        
        if models.facebook.facebook_page.FacebookPage.objects.filter(page_id=page_id).exists():
            facebook_page = models.facebook.facebook_page.FacebookPage.objects.get(page_id=page_id)
            facebook_page.name = page_name
            facebook_page.token = page_token
            facebook_page.token_update_at = datetime.now()
            facebook_page.image = page_image
            facebook_page.save()
        else:
            facebook_page = models.facebook.facebook_page.FacebookPage.objects.create(
                page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), image=page_image)
            facebook_page.save()

        if facebook_page not in user_subscription.facebook_pages.all():
            user_subscription.facebook_pages.add(facebook_page)

def bind_instagram_profiles(request, user_subscription):
    
    token, = lib.util.getter.getdata(request,('accessToken',), required=True)
    status_code, response = service.facebook.user.get_me_accounts(token)

    if status_code != 200:
        raise lib.error_handle.error.api_error.ApiCallerError("helper.api_fb_get_accounts_error")
        
    business_id_of_binded_pages = []
    
    for item in response.get('data',[]):
        page_token = item.get('access_token')
        page_id = item.get('id')
        page_name = item.get('name')

        status_code, business_profile_response  = service.facebook.page.get_page_business_profile(page_token=page_token, page_id=page_id)

        if status_code != 200:
            print('get profile error')
            continue

        business_id = business_profile_response.get("instagram_business_account",{}).get("id")
        
        if not business_id:
            print('no business id')
            continue
        
        status_code, profile_info_response = service.instagram.profile.get_profile_info(page_token, business_id)
        # status_code, profile_info_response = api_ig_get_profile_info(page_token, business_id)
        profile_name = profile_info_response.get('name')
        profile_username = profile_info_response.get('username')
        profile_pricure = profile_info_response.get('profile_picture_url')
        
        if models.instagram.instagram_profile.InstagramProfile.objects.filter(business_id=business_id).exists():
            instagram_profile = models.instagram.instagram_profile.InstagramProfile.objects.get(business_id=business_id)
            instagram_profile.connected_facebook_page_id = page_id
            instagram_profile.name = profile_name
            instagram_profile.username = profile_username
            instagram_profile.token = page_token
            instagram_profile.token_update_at = datetime.now()
            # instagram_profile.token_update_by = api_user.facebook_info['id']
            instagram_profile.image = profile_pricure
            instagram_profile.save()
        else:
            instagram_profile = models.instagram.instagram_profile.InstagramProfile.objects.create(
                business_id=business_id, connected_facebook_page_id=page_id, name=profile_name, token=page_token, token_update_at=datetime.now(), image=profile_pricure)
            instagram_profile.save()

        if instagram_profile not in user_subscription.instagram_profiles.all():
            user_subscription.instagram_profiles.add(instagram_profile)

def bind_youtube_channels(request, user_subscription):

    code, = lib.util.getter.getdata(request,("code",), required=True)

    response_code, response = service.google.user.get_token(code, request.META['HTTP_ORIGIN'], 
        settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER, 
        settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER)

    if not response_code / 100 == 2:
        lib.error_handle.error.api_error.ApiCallerError('get google token fail')


    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")

    status_code, response = service.youtube.channel.get_list_channel_by_token(access_token)

    if status_code != 200:
        raise lib.error_handle.error.api_error.ApiCallerError("helper.api_yt_list_channel_error")
    
    if not response.get("items"):
        raise lib.error_handle.error.api_error.ApiCallerError("helper.no_channel_found")

    #TODO handle next page token
    for item in response['items']:

        # channel_etag = item.get('etag')
        channel_id = item.get('id')
        snippet = item.get('snippet')
        title = snippet.get('title')
        picture = snippet.get('thumbnails',{}).get('default',{}).get('url',{})
        
        if models.youtube.youtube_channel.YoutubeChannel.objects.filter(channel_id=channel_id).exists():
            youtube_channel = models.youtube.youtube_channel.YoutubeChannel.objects.get(channel_id=channel_id)
            youtube_channel.name = title
            youtube_channel.token = access_token
            youtube_channel.refresh_token = refresh_token
            youtube_channel.token_update_at = datetime.now()
            youtube_channel.image = picture
            youtube_channel.save()
        else:
            youtube_channel = models.youtube.youtube_channel.YoutubeChannel.objects.create(
                channel_id=channel_id, 
                name=title, 
                token=access_token, 
                refresh_token=refresh_token,
                token_update_at=datetime.now(), 
                image=picture
            )
            youtube_channel.save()

        if youtube_channel not in user_subscription.youtube_channels.all():
            user_subscription.youtube_channels.add(youtube_channel)

def bind_twitch_channels(request, user_subscription):

    code, = lib.util.getter.getdata(request,("code",), required=True)

    response_code, response = service.twitch.twitch.get_token(code)
    if not response_code / 100 == 2:
        lib.error_handle.error.api_error.ApiCallerError('get twitch token fail')

    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")

    response_code, response = service.twitch.twitch.get_user(access_token)
    if not response_code / 100 == 2:
        lib.error_handle.error.api_error.ApiCallerError('get twitch user detail fail')
    
    channel_name = response.get("preferred_username")

    response_code, response = service.twitch.twitch.get_user_info(access_token, channel_name)
    if not response_code / 100 == 2:
        lib.error_handle.error.api_error.ApiCallerError('get twitch user info fail')
    
    image = response.get("data")[0].get("profile_image_url")

    if models.twitch.twitch_channel.TwitchChannel.objects.filter(name=channel_name).exists():
        twitch_channel = models.twitch.twitch_channel.TwitchChannel.objects.get(name=channel_name)
        twitch_channel.name = channel_name
        twitch_channel.user_name = channel_name
        twitch_channel.token = access_token
        twitch_channel.refresh_token = refresh_token
        twitch_channel.token_update_at = datetime.now()
        twitch_channel.image = image
        twitch_channel.save()
    else:
        twitch_channel = models.twitch.twitch_channel.TwitchChannel.objects.create(
            name=channel_name, 
            user_name=channel_name, 
            token=access_token, 
            refresh_token=refresh_token,
            token_update_at=datetime.now(), 
            image=image
        )
        twitch_channel.save()

    if twitch_channel not in user_subscription.twitch_channels.all():
        user_subscription.twitch_channels.add(twitch_channel)