import pickle
import platform
import time
import functools, logging, traceback
import lib
import service
from django.conf import settings
import os
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


class FacebookCrawler():
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')  # 啟動Headless 無頭
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # if "Linux" in platform.platform():
        #     chrome_driver_path = os.path.join(settings.BASE_DIR, 'chromedriver')
        # self.chromeService = Service(executable_path=chrome_driver_path)

        self.driver = None #套用設定
        self.wait = None
        self.actions = None
        
        self.login_url = "https://m.facebook.com/"
        self.page_url = ""
        
        self.email = settings.FACEBOOK_TEST_ACOOUNT['EMAIL']
        self.password = settings.FACEBOOK_TEST_ACOOUNT['PASSWORD']
        self.cookies = None
        self.cookies_path = os.path.join(settings.BASE_DIR, "cookies/facebook_cookie.pkl")
        self.is_login = False
        self.save_login = True
        
    def create_driver(self):
        print("remote")
        self.driver = webdriver.Remote(command_executor='http://localhost:4444', options=self.chrome_options)
        return self.driver
    
    def create_action_object(self):
        if self.driver:
            self.actions = ActionChains(self.driver)
        return self.actions
    
    def create_wait_object(self):
        if self.driver:
            self.wait = WebDriverWait(self.driver, 5)
        return self.wait
    
    def get_driver(self):
        return self.driver
    
    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))
        print(f"save facebook cookies to {self.cookies_path}")
        
    def find_cookies(self):
        if os.path.exists(self.cookies_path):
            cookies = pickle.load(open(self.cookies_path, "rb"))
            return cookies
        else:
            return None
        
    def login(self, validate=False):
        """
        """
        pass
        
    def validate_user(self):
        """
        """
        pass
        
    def start(self):
        """
        """
        pass