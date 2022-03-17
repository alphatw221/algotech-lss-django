from attr import field
from backend.api.facebook._fb_api_caller import FacebookApiCaller


def api_fb_get_page_posts(page_token: str, page_id: str):
    params = {
        'limit': 100
    }
    ret = FacebookApiCaller(f'{page_id}/posts', bearer_token=page_token,
                            params=params).get()
    return ret


def api_fb_post_page_message(page_token: str, page_id: str, recipient_id: str, message_text: str):
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    ret = FacebookApiCaller(f'{page_id}/messages', bearer_token=page_token,
                            data=data).post()
    return ret


def api_fb_get_page_picture(page_token: str, page_id: str, height: int, width: int):
    params = {
        'redirect': 0,
        'height': height,
        'width': width,
    }
    ret = FacebookApiCaller(f'v12.0/{page_id}/picture', bearer_token=page_token,
                            params=params).get()
    return ret


def api_fb_get_page_admin(page_token: str, page_id: str, user_id: str):

    ret = FacebookApiCaller(
        f'v2.2/{page_id}/roles', bearer_token=page_token).get()
    return ret

def api_fb_get_page_business_profile(page_token: str, page_id:str):
    params = {
        "fields":"instagram_business_account"
    }
    ret = FacebookApiCaller(f'v13.0/{page_id}', bearer_token=page_token,
                            params=params).get()
    return ret
# fetch(`https:\/\/graph.facebook.com/v12.0/me/accounts?fields=instagram_business_account%7Busername%2Cid%2Clive_media%7Bmedia_url%2Cid%7D%7D&access_token=${GS.fb_user_access_token}`, {
#                 method: 'GET', mode: 'cors', headers: new Headers({ 'Content-Type': 'application/json' })
#             }).then(res => {if (!res.ok) throw res; return res.json(); }).then(data => {
#                 const sort = data.data.filter(v => v.instagram_business_account && v.instagram_business_account.live_media).map(v => {return v.instagram_business_account})
#                 console.log(sort)
#                 if (!sort.length) {alert('You have no one ig live post now.')} else {const modal = document.getElementById('ig_modal'); let html = '';
#                     sort.forEach(v => v.live_media.data.forEach(vl => html += `
#                     <div class='row'><div class='col s12 m7' style='cursor: pointer;' onclick='insert_ig_post_id(${vl.id}n)'><div class='card'>
#                         <div class='card-image'><img src='${vl.media_url}'></div><div class='card-content'><span class='card-title'>${v.username}</span></div>
#                     </div></div></div>`)); modal.querySelector('.content').innerHTML = html; $(modal).modal(); $(modal).modal('open'); }
#             }).catch(error => {switch(error.status) {
#                 case 500: alert('Oops! Something went wrong when fetch data. Facebook officail api has crashed.'); break
#                 case 401: alert('You have no permission to access this fb (ig) asset.'); break
#             }})


    params={

    }