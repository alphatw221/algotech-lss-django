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
from selenium.webdriver.support import expected_conditions as EC


class FacebookCrawler():
    def __init__(self, open_browser=False, chromedriver_path=None):
        self.chrome_options = webdriver.ChromeOptions()
        if not open_browser:
            self.chrome_options.add_argument('--headless')  # 啟動Headless 無頭
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.chromeService = Service(executable_path=chromedriver_path)
        self.chromedriver_path = chromedriver_path
        self.driver = None #套用設定
        self.wait = None
        self.actions = None
        
        self.login_url = "https://m.facebook.com/"
        self.page_url = ""
        
        self.email = settings.FACEBOOK_TEST_ACOOUNT['EMAIL']
        self.password = settings.FACEBOOK_TEST_ACOOUNT['PASSWORD']
        self.cookies = None
        self.cookies_path = os.path.join(settings.BASE_DIR, "pkl/cookies/facebook_cookie.pkl")
        self.is_login = False
        self.save_login = False
        
    def create_driver(self):
        
        if self.chromedriver_path:
            print("local")
            print(self.chromedriver_path)
            service = Service(executable_path=self.chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        else:
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
    
    def quit_driver(self):
        self.driver.quit()
        
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
        print("validate_user")
        try:
            print("check if Go to App button shows up")
            # check if Go to App button shows up, if yes, pass validation
            go_to_app_button = self.driver.find_element(By.CSS_SELECTOR, "button[value='Go to App']")
            if go_to_app_button:
                self.save_login = True
        except:
            print(traceback.format_exc())
            
        if not self.save_login:
            print("regular login check")
            try:
                self.driver.find_element(By.CSS_SELECTOR, "input[value='regular_login']")
                ok_button = self.driver.find_element(By.CSS_SELECTOR, "button[value='OK']")
                if ok_button:
                    self.actions.click(ok_button).perform()
                    self.save_login = True
            except:
                print(traceback.format_exc())
            
        if not self.save_login:
            print("enter check point")
            try:
                check_point_button = self.driver.find_element(By.ID, "checkpointSubmitButton-actual-button")
                if check_point_button:
                    self.actions.click(check_point_button).perform()
            except:
                print(traceback.format_exc())
                
        if not self.save_login:
            print("new page identity double check")
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
            print("header identity double check")
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
        """
        """
        pass