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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class RenewFacebookCookiesCrawler(FacebookCrawler):
    
        
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