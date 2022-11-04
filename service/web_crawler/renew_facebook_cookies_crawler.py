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


class RenewFacebookCookiesCrawler(FacebookCrawler):
    def __init__(self, open_browser=False, chromedriver_path=None):
        super().__init__(open_browser, chromedriver_path)
        
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
    
    def start(self):
        try:
            self.create_driver()
            self.create_wait_object()
            self.create_action_object()
            self.login()
            self.driver.quit()
        except Exception as e:
            print(traceback.format_exc())
            if self.driver:
                self.driver.quit()