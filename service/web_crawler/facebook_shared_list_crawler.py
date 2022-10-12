import pickle
import platform
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
from service.web_crawler.facebook_crawler import FacebookCrawler
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


class FacebookSharedListCrawler(FacebookCrawler):
    def __init__(self, page_username, target_post_id, lang="en", chrome_driver_path=os.path.join(settings.BASE_DIR, 'chromedriver.exe')):
        super().__init__()
        self.page_url = f'https://m.facebook.com/{page_username}/'
        self.target_post_id = target_post_id
        self.post_reference_id = ""
        self.post_shared_list_url = "https://m.facebook.com/browse/shares?id="
        
        self.lang_map = {
            "zh_hant": "中文(台灣)",
            "en": "English (US)",
            "zh_hans": "中文(简体)",
            "vi": "Tiếng Việt"
        }
        self.lang = self.lang_map.get(lang)
    
    
    
    def login_with_cookies(self, cookies):
        print("login with cookies")
        for c in cookies:
            self.driver.add_cookie(c)
        self.is_login = True
        self.driver.refresh()
#         self.validate_user()
        
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
        self.save_cookies()
    
    def validate_user(self):
        print("validate_user")
        # check if page pops up log in with one tap
        try:
            self.driver.find_element(By.CSS_SELECTOR, "input[value='regular_login']")
            ok_button = self.driver.find_element(By.CSS_SELECTOR, "button[value='OK']")
            self.actions.click(ok_button).perform()
            self.save_login = True
        except:
            pass
            
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
                pass
            
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
                pass
            
    def switch_language(self):
        self.driver.get("https://m.facebook.com/language/")
        current_language = self.driver.find_element(By.CLASS_NAME, "_5551")
        
    def get_post_shared_list_url(self):
        found = False
        count = 0
        while not found:
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            article = self.wait.until(
                    EC.visibility_of_element_located((By.TAG_NAME, "article"))
                )
            if article:
                articles = self.driver.find_elements(By.XPATH, "//article")
               
                for article in articles:
                    if self.post_reference_id:
                        break
                    video_data = json.loads(article.get_attribute("data-ft"))
                    if video_data.get('video_id', None) != self.target_post_id:
                        continue
                    print(video_data)
                    post_data = json.loads(article.get_attribute("data-store"))
                    self.post_reference_id = str(post_data.get("feedback_target",""))
                    found = True
#                     for key,value in post_data.items():
#                         if key == "share_id":
# #                             print(key)
# #                             print(value)
#                             if ":" not in str(value):
#                                 post_id = str(value)
#                             else:
#                                 post_id = value.split(":")[1]
#                             if post_id != self.target_post_id:
#                                 break

#                         if key == "feedback_target":
# #                             print(key)
# #                             print(value)
#                             self.post_reference_id = str(value)
#                             break
            if count == 20:
                found = True
            count += 1
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
            return {}