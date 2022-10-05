import pickle
import time
from typing import OrderedDict
import functools, logging, traceback
from api import models
import service
from django.conf import settings
import os
import random
import lib
from api import models
from collections import OrderedDict
import json
import arrow
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.color import Color
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


class LuckyDrawCandidate():

    def __init__(self,platform, customer_id, comment_id=None, customer_name="", customer_image="", draw_type=None, prize=None):
        self.comment_id = comment_id
        self.platform = platform
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_image = customer_image
        self.draw_type = draw_type
        self.prize = prize

    def __hash__(self) -> int:
        return (self.platform, self.customer_id).__hash__()


    def __eq__(self, __o: object) -> bool:
        try:
            if type(__o) in [dict,OrderedDict]:
                return self.platform ==__o.get('platform') and self.customer_id==__o.get('customer_id')
            return self.platform == __o.platform and self.customer_id==__o.customer_id
        except Exception:
            return False

    def to_dict(self):
        return {'platform':self.platform,'customer_id':self.customer_id,'customer_name':self.customer_name,'customer_image':self.customer_image,'draw_type':self.draw_type,'prize':self.prize}

class CandidateSetGenerator():

    @classmethod
    def get_candidate_set(cls):
        return set()


class KeywordCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw, limit=1000):
        
        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()
        campaign_comments = models.campaign.campaign_comment.CampaignComment.objects.filter(
            campaign=campaign,
            # message=keyword,
            message__contains=lucky_draw.comment,
        )[:limit]

        for campaign_comment in campaign_comments:

            candidate = LuckyDrawCandidate(
                platform=campaign_comment.platform, 
                customer_id=campaign_comment.customer_id, 
                comment_id = campaign_comment.id,
                customer_name=campaign_comment.customer_name,
                customer_image=campaign_comment.image,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set

class CommentCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw, limit=1000):
        
        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()
        campaign_comments = models.campaign.campaign_comment.CampaignComment.objects.filter(
            campaign=campaign,
        )[:limit]

        for campaign_comment in campaign_comments:

            candidate = LuckyDrawCandidate(
                platform=campaign_comment.platform, 
                customer_id=campaign_comment.customer_id, 
                comment_id = campaign_comment.id,
                customer_name=campaign_comment.customer_name,
                customer_image=campaign_comment.image,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set


class LikesCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw, limit=1000):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()
        
        likes_user_list=[]
        response = {}
        
        if campaign.facebook_page_id and models.facebook.facebook_page.FacebookPage.objects.filter(id=campaign.facebook_page_id).exists():
            facebook_page = models.facebook.facebook_page.FacebookPage.objects.get(id=campaign.facebook_page_id)
            post_id=campaign.facebook_campaign.get('post_id')
            token=facebook_page.token   

            code, response = service.facebook.post.get_post_likes(token, facebook_page.page_id, post_id, after=None, limit=limit)
            # print(code)
            # print(response)
            if code!=200 :
                raise lib.error_handle.error.api_error.ApiVerifyError('helper.fb_api_fail')
            # likes_user_list += [user.get('name') for user in response.get('data',[])]
            # print(likes_user_list)
        # campaign_comments = models.campaign.campaign_comment.CampaignComment.objects.filter(
        #     campaign=campaign,
        #     customer_name__in=likes_user_list
        # )[:limit]

        for user in response.get('data',[]):
        
            candidate = LuckyDrawCandidate(
                platform='facebook', 
                customer_id=user.get('id'),     #ASID over here!! might have some issues 
                customer_name=user.get('name'),
                customer_image=user.get('pic_large'),
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set



class ProductCandidateSetGenerator(CandidateSetGenerator):
    
    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()

        order_products = models.order.order_product.OrderProduct.objects.filter(campaign=campaign, campaign_product=lucky_draw.campaign_product, platform__isnull=False)
        for order_product in order_products:
            img_url = models.order.pre_order.PreOrder.objects.get(customer_id=order_product.customer_id, campaign=campaign.id).customer_img
            candidate = LuckyDrawCandidate(

                platform=order_product.platform, 
                customer_id=order_product.customer_id, 
                customer_name=order_product.customer_name,
                customer_image=img_url,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set


class PurchaseCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()

        orders = models.order.order.Order.objects.filter(campaign=campaign, platform__isnull=False)
        pre_orders = models.order.pre_order.PreOrder.objects.filter(campaign=campaign,subtotal__gt=0, platform__isnull=False)
        for order in orders:
            candidate = LuckyDrawCandidate(
                platform=order.platform, 
                customer_id=order.customer_id, 
                customer_name=order.customer_name,
                customer_image=order.customer_img,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)
        
        for pre_order in pre_orders:
            candidate = LuckyDrawCandidate(
                platform=pre_order.platform, 
                customer_id=pre_order.customer_id, 
                customer_name=pre_order.customer_name,
                customer_image=pre_order.customer_img,
                draw_type=lucky_draw.type,
                prize=lucky_draw.prize.name)

            if not lucky_draw.repeatable and candidate in winner_list:
                continue

            candidate_set.add(candidate)

        return candidate_set

class SharedPostCandidateSetGenerator(CandidateSetGenerator):

    @classmethod
    def get_candidate_set(cls, campaign, lucky_draw, limit=1000):

        winner_list = campaign.meta.get('winner_list',[])
        candidate_set = set()
        users_like_and_comment_set = set()
        response = {}
        
        if campaign.facebook_page_id and models.facebook.facebook_page.FacebookPage.objects.filter(id=campaign.facebook_page_id).exists():
            facebook_page = models.facebook.facebook_page.FacebookPage.objects.get(id=campaign.facebook_page_id)
            post_id=campaign.facebook_campaign.get('post_id')
            token=facebook_page.token   

            code, response = service.facebook.post.get_post(token, facebook_page.page_id, post_id)
            if code!=200 :
                raise lib.error_handle.error.api_error.ApiVerifyError('helper.fb_api_fail')
        
        shares_count = response.get("shares", {}).get("count", 0)
        # print(shares_count)
        if not shares_count:
            return candidate_set
        
        
        shared_user_name_set = lucky_draw.meta.get("shared_post_data", {})
        print("shared_user_name_set", shared_user_name_set)
        if not shared_user_name_set:
            return candidate_set
        
        like_data = response.get("likes",{}).get("data",[])
        # print(like_data)
        like_user_id_set = set([i["id"] for i in like_data])
        
        comments_data = models.campaign.campaign_comment.CampaignComment.objects.filter(
            campaign=campaign, platform="facebook")
        # campaign_comments_user_id_set = set(comments_data.values_list("customer_id", flat=True))
        campaign_comments_user_name_set = set(comments_data.values_list("customer_name", flat=True))
        print("campaign_comments_user_name_set", campaign_comments_user_name_set)
        
        if len(campaign_comments_user_name_set):
            users_shared_and_comment_set = shared_user_name_set.intersection(campaign_comments_user_name_set)
            campaign_comments = comments_data.filter(customer_name__in=list(users_shared_and_comment_set))
            for campaign_comment in campaign_comments:

                candidate = LuckyDrawCandidate(
                    platform=campaign_comment.platform, 
                    customer_id=campaign_comment.customer_id, 
                    comment_id = campaign_comment.id,
                    customer_name=campaign_comment.customer_name,
                    customer_image=campaign_comment.image,
                    draw_type=lucky_draw.type,
                    prize=lucky_draw.prize.name)

                if not lucky_draw.repeatable and candidate in winner_list:
                    continue

                candidate_set.add(candidate)
        
        # if len(like_user_id_set) and len(campaign_comments_user_id_set):
        #     users_like_and_comment_set = like_user_id_set.intersection(campaign_comments_user_id_set)
        #     data = []
        #     for i in like_data:
        #         if i["id"] in users_like_and_comment_set and i["id"] not in data:
        #             data.append(i)
        #     for user in data:
        #         candidate = LuckyDrawCandidate(
        #             platform='facebook', 
        #             customer_id=user.get('id'),     #ASID over here!! might have some issues 
        #             customer_name=user.get('name'),
        #             customer_image=user.get('pic_large'),
        #             draw_type=lucky_draw.type,
        #             prize=lucky_draw.prize.name)

        #         if not lucky_draw.repeatable and candidate in winner_list:
        #             continue
                
        #         candidate_set.add(candidate)
                
        # elif not len(like_user_id_set) and not len(campaign_comments_user_id_set):
        #     return candidate_set
        
        # elif len(like_user_id_set):
        #     users_like_and_comment_set = like_user_id_set
        #     data = []
        #     for i in like_data:
        #         if i["id"] in users_like_and_comment_set and i["id"] not in data:
        #             data.append(i)
        #     for user in data:
        #         candidate = LuckyDrawCandidate(
        #             platform='facebook', 
        #             customer_id=user.get('id'),     #ASID over here!! might have some issues 
        #             customer_name=user.get('name'),
        #             customer_image=user.get('pic_large'),
        #             draw_type=lucky_draw.type,
        #             prize=lucky_draw.prize.name)

        #         if not lucky_draw.repeatable and candidate in winner_list:
        #             continue
        #         candidate_set.add(candidate)
                
        # elif len(campaign_comments_user_id_set):
        #     users_like_and_comment_set = campaign_comments_user_id_set
        #     campaign_comments = []
        #     for i in comments_data:
        #         if i.id in users_like_and_comment_set and i.id not in campaign_comments:
        #             campaign_comments.append(i)
        #     for campaign_comment in campaign_comments:

        #         candidate = LuckyDrawCandidate(
        #             platform=campaign_comment.platform, 
        #             customer_id=campaign_comment.customer_id, 
        #             comment_id = campaign_comment.id,
        #             customer_name=campaign_comment.customer_name,
        #             customer_image=campaign_comment.image,
        #             draw_type=lucky_draw.type,
        #             prize=lucky_draw.prize.name)

        #         if not lucky_draw.repeatable and candidate in winner_list:
        #             continue

        #         candidate_set.add(candidate)
        
        num_of_candidate = len(candidate_set) if shares_count > len(candidate_set) else shares_count
        candidates = random.sample(list(candidate_set), num_of_candidate)
        
        return candidates
    
class LuckyDraw():

    @classmethod
    def draw_from_candidate(cls, campaign, campaign_product, candidate_set=set(), num_of_winner=1):
        if not candidate_set:
            print('no candidate')
            return []
        num_of_winner = len(candidate_set) if num_of_winner > len(candidate_set) else num_of_winner
        winners = random.sample(list(candidate_set), num_of_winner)
        if not winners:
            print('no winners')
            return []
        
        campaign_winner_list = campaign.meta.get('winner_list',[])
        winner_list = []

        
        for winner in winners:                                              #multithread needed
            try:
                cls.__add_product(campaign, winner, campaign_product)
                cls.__announce(campaign, winner, campaign_product)
                cls.__send_private_message(campaign, winner, campaign_product)
                winner_dict = winner.to_dict()
                # if winner not in campaign_winner_list:
                campaign_winner_list.append(winner_dict)

                winner_list.append(winner_dict)
            except Exception:
                pass
            
        campaign.meta['winner_list']=campaign_winner_list
        campaign.save()

        return winner_list

    @classmethod
    def __add_product(
        cls, 
        campaign: models.campaign.campaign.Campaign, 
        winner:LuckyDrawCandidate, 
        campaign_product:models.campaign.campaign_product.CampaignProduct ):

            if models.order.pre_order.PreOrder.objects.filter(
                campaign=campaign, platform=winner.platform, customer_id=winner.customer_id, customer_name=winner.customer_name).exists():
                pre_order = models.order.pre_order.PreOrder.objects.get(
                    campaign=campaign, platform=winner.platform, customer_id=winner.customer_id, customer_name=winner.customer_name)
            else:
                platform_id_dict = {
                    'facebook': campaign.facebook_page.id if campaign.facebook_page else None,
                    'youtube': campaign.youtube_channel.id if campaign.youtube_channel else None,
                    'instagram': campaign.instagram_profile.id if campaign.instagram_profile else None
                }
                pre_order = models.order.pre_order.PreOrder.objects.create(
                    customer_id=winner.customer_id, 
                    customer_name=winner.customer_name, 
                    customer_img=winner.customer_image, 
                    campaign = campaign, 
                    platform=winner.platform, 
                    platform_id=platform_id_dict.get(winner.platform))

            print ('campaign_product', campaign_product)

            if prize_product := pre_order.products.get(str(campaign_product.id), None):
                qty = prize_product['qty'] + 1
                lib.helper.order_helper.PreOrderHelper.update_product(api_user=None, pre_order_id=pre_order.id, 
                    order_product_id=prize_product.get('order_product_id'),qty=qty)
            else:
                lib.helper.order_helper.PreOrderHelper.add_product(api_user=None, pre_order_id=pre_order.id, campaign_product_id=campaign_product.id,qty=1)
            
    

    @classmethod
    def __announce(cls, 
    campaign: models.campaign.campaign.Campaign, 
    winner: LuckyDrawCandidate, 
    campaign_product:models.campaign.campaign_product.CampaignProduct):
        
        text = lib.i18n.campaign_announcement.get_campaign_announcement_lucky_draw_winner(campaign_product.name, winner.customer_name, lang=campaign.lang)


        if (facebook_page := campaign.facebook_page):
            service.facebook.post.post_page_comment_on_post(facebook_page.token, campaign.facebook_campaign.get('post_id'), text)
        

        if (youtube_channel := campaign.youtube_channel):
            service.youtube.live_chat.post_live_chat_comment(youtube_channel.token, campaign.youtube_campaign.get('live_chat_id'), text)

    @classmethod
    def __send_private_message(cls, 
    campaign: models.campaign.campaign.Campaign, 
    winner: LuckyDrawCandidate, 
    campaign_product:models.campaign.campaign_product.CampaignProduct):

        text = lib.i18n.campaign_announcement.get_campaign_announcement_lucky_draw_winner(campaign_product.name, winner.customer_name, lang=campaign.lang)  #temp

        if (campaign.instagram_profile and winner.platform=='instagram'):
            service.instagram.chat_bot.post_page_message_chat_bot(campaign.instagram_profile.connected_facebook_page_id, campaign.instagram_profile.token, winner.customer_id, text)


    
    @classmethod
    def __get_image(cls, winner:LuckyDrawCandidate):
        pass



def draw(campaign, lucky_draw):
    
    if lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_KEYWORD:
        candidate_set = lib.helper.lucky_draw_helper.KeywordCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_LIKE:
        candidate_set = lib.helper.lucky_draw_helper.LikesCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_PRODUCT:
        candidate_set = lib.helper.lucky_draw_helper.ProductCandidateSetGenerator.get_candidate_set(campaign, lucky_draw)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_PURCHASE:
        candidate_set = lib.helper.lucky_draw_helper.PurchaseCandidateSetGenerator.get_candidate_set(campaign, lucky_draw)
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_LIKE_AND_COMMENT:

        fb_like_candidate_set = lib.helper.lucky_draw_helper.LikesCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
        comment_candidate_set = lib.helper.lucky_draw_helper.CommentCandidateSetGenerator.get_candidate_set(campaign, lucky_draw, limit=100)
        candidate_set = fb_like_candidate_set.intersection(comment_candidate_set)
    
    elif lucky_draw.type == models.campaign.campaign_lucky_draw.TYPE_POST:
        candidate_set = lib.helper.lucky_draw_helper.SharedPostCandidateSetGenerator.get_candidate_set(campaign, lucky_draw)
    else:
        return []
    return lib.helper.lucky_draw_helper.LuckyDraw.draw_from_candidate(campaign, lucky_draw.prize,  candidate_set=candidate_set, num_of_winner=lucky_draw.num_of_winner)


class FacebookSharedListCrawler():
    def __init__(self, page_username, target_post_id, chrome_driver_path=os.path.join(settings.BASE_DIR, 'chromedriver.exe')):
        self.chrome_options = Options() 
        self.chrome_options.add_argument('--headless')  # 啟動Headless 無頭
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.chromeService = Service(executable_path=chrome_driver_path)

        self.driver = None #套用設定
        self.wait = None
        self.actions = None
        
        self.login_url = "https://m.facebook.com/"
        self.page_url = f'https://m.facebook.com/{page_username}/'
        self.target_post_id = target_post_id
        
        self.post_reference_id = ""
        self.post_shared_list_url = "https://m.facebook.com/browse/shares?id="
        
        self.email = "twadmin@algotech.app"
        self.password = "algoFB2021"
        self.loop_count = 0
        self.save_login = False
        self.is_login = False
        self.cookies = None
        self.cookies_path = os.path.join(settings.BASE_DIR, "cookies/facebook_cookie.pkl")
        
    def create_driver(self):
        self.driver = webdriver.Chrome(options=self.chrome_options, service= self.chromeService)
        return self.driver
    
    def create_action_object(self):
        if self.driver:
            self.actions = ActionChains(self.driver)
        return self.actions
    
    def create_wait_object(self):
        if self.driver:
            self.wait = WebDriverWait(self.driver, 3)
        return self.wait
    
    def get_driver(self):
        return self.driver
    
    def find_cookies(self):
        if os.path.exists(self.cookies_path):
            cookies = pickle.load(open(self.cookies_path, "rb"))
            return cookies
        else:
            return None
    
    def login_with_cookies(self, cookies):
        print("login with cookies")
        for c in cookies:
            self.driver.add_cookie(c)
        self.is_login = True
        self.driver.refresh()
        # self.validate_user()
        
    def login(self, validate=False):
        print("login")
        count = 0
        while not self.is_login and count <= 4:
            if not validate:
                self.driver.get(self.login_url)
            email_input = self.driver.find_element(By.ID, "m_login_email")
            pass_input = self.driver.find_element(By.ID, "m_login_password")
            login_button = self.driver.find_element(By.NAME, "login")
            self.actions.send_keys_to_element(email_input, self.email)
            self.actions.send_keys_to_element(pass_input, self.password)
            self.actions.click(login_button)
            self.actions.perform()
            count += 1
            self.is_login = True
        time.sleep(2)
        self.validate_user()
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))
    
    def validate_user(self):
        print("validate_user")
        # check if page pops up log in with one tap
        try:
            self.driver.find_element(By.CSS_SELECTOR, "input[value='regular_login']")
            ok_button = self.driver.find_element(By.CSS_SELECTOR, "button[value='OK']")
            self.actions.click(ok_button).perform()
            self.save_login = True
        except:
            print(traceback.format_exc())
            
        if not self.save_login:
            # check new page identity double check
            try:
                my_profile = self.driver.find_element(By.CSS_SELECTOR, f"div[role='button']")
                self.actions.click(my_profile).perform()

                pass_input = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "pass"))
                )
                self.actions.send_keys_to_element(pass_input, self.password)
                login_button = self.driver.find_element(By.CSS_SELECTOR , "button[type='submit']")
                self.actions.click(login_button).perform()
                self.save_login = True
            except:
                print(traceback.format_exc())
            
        if not self.save_login:
            # check header identity double check
            try:
                login_button = self.driver.find_element(By.CSS_SELECTOR , "button[type='submit']")
                self.actions.click(login_button).perform()
                pass_input = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "pass"))
                )
                self.actions.send_keys_to_element(pass_input, self.password)
                login_button = self.driver.find_element(By.CSS_SELECTOR , "button[type='submit']")
                self.actions.click(login_button).perform()
                self.save_login = True
            except:
                print(traceback.format_exc())
    def get_post_shared_list_url(self):
        while self.loop_count <= 3:
            self.loop_count += 1
            self.driver.execute_script("window.scrollTo(100,document.body.scrollHeight);")

            article = self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            if article:
                articles = self.driver.find_elements(By.XPATH, "//article")
                for article in articles:
                    if self.post_reference_id:
                        break
                    post_data = json.loads(article.get_attribute("data-store"))
                    for key,value in post_data.items():
                        if key == "share_id":
                            if type(value) == int:
                                post_id = str(value)
                            else:
                                post_id = value.split(":")[1]
                            if post_id != self.target_post_id:
                                break

                        if key == "feedback_target":
                            self.post_reference_id = str(value)
                            break

            self.loop_count += 1
        print(self.post_shared_list_url + self.post_reference_id)
        return self.post_shared_list_url + self.post_reference_id
        
    def expand_all(self):
        try:
            while True:
                see_more_button = self.driver.find_element(By.ID, "m_more_item")
                if see_more_button:
                    self.actions.click(see_more_button).perform()
        except NoSuchElementException:
            print("Element is not present")
            
    def collect_names(self):
        names = set([el.text for el in self.driver.find_elements(By.TAG_NAME, "strong")])
        return names
    
    def start(self):
        start = arrow.now()
        try:
            self.create_driver()
            self.create_wait_object()
            self.create_action_object()
            
            cookies = self.find_cookies()
            if cookies:
                self.driver.get(self.page_url)
                self.login_with_cookies(cookies)
            else:    
                self.login()
                self.driver.get(self.page_url)
                
            post_shared_list_url = self.get_post_shared_list_url()
            self.driver.get(post_shared_list_url)
            
            if not self.save_login:
                self.validate_user()
            self.expand_all()
            name_list = self.collect_names()
            end = arrow.now()
            print(f"Spent: {end - start}")
            self.driver.quit()
            return name_list
        except Exception as e:
            print(traceback.format_exc())
            if self.driver:
                self.driver.quit()
            return None

