import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import unittest
import HtmlTestRunner
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By



# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailOTPFetcher:
    def __init__(self):
        self.service = self.get_gmail_service()

    def get_gmail_service(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('gmail', 'v1', credentials=creds)
        return service

    def get_otp_from_email(self):
        try:
            query = 'subject:"[Wind.App] OTP:"'
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])

            if not messages:
                print("No new emails found.")
                return None

            print(f"Found {len(messages)} emails. Fetching the latest one.")

            message = self.service.users().messages().get(userId='me', id=messages[0]['id']).execute()
            
            if 'data' in message['payload']['body']:
                msg_str = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
            else:
                parts = message['payload']['parts']
                msg_str = ""
                for part in parts:
                    if 'data' in part['body']:
                        msg_str += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

            msg_soup = BeautifulSoup(msg_str, 'html.parser')
            otp = None

            text = msg_soup.get_text()
            lines = text.split('\n')
            for line in lines:
                if 'Verification Code:' in line:
                    otp = line.split('Verification Code:')[1].strip()
                    print(f"The OTP is: {otp}")
                    break

            return otp
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

class WindAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()
        cls.fetcher = GmailOTPFetcher()

    def test_01_signup(self):
        driver = self.driver
        driver.get("https://business.wind.app/signup")
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "email"))).send_keys("sadikun22123+SignUp@gmail.com")
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Continue']"))).click()
        time.sleep(30)
        otp = self.fetcher.get_otp_from_email()
        self.signUpWithOTP(driver, otp)
        self.ManageProfile(driver)

    def test_02_login(self):
        driver = self.driver
        driver.get("https://business.wind.app/login")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "email"))).send_keys("sadikun22123@gmail.com")
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Continue']"))).click()
        time.sleep(30)
        otp = self.fetcher.get_otp_from_email()
        self.logWithOTP(driver, otp)
        try:
                   
                    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'Home')]")))

                    signup_successful = True
        except TimeoutException:
                        signup_successful = False
                        print("logIn not Successfull")

        self.assertTrue(signup_successful, "LogIn Succeeful")
    def signUpWithOTP(self, driver, otp):
        otp_digits = list(otp)  
        k=1
        for i, digit in enumerate(otp_digits):
            # print(digit)
            # print(k)
        
            WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, f"//div[@class='pincode-input-container']//input[{k}]"))).send_keys(digit)
            k=  k+1
            # print(digit)
            time.sleep(2)
        time.sleep(10)
        for l in range(1, 5):
            WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//body/div[@id='__next']/div[@class='sc-gkKZNe DQLPr']/main[@class='sc-dkmUuB dgmJiL th-light']/aside[@class='sc-kzqdkY fZHYOx']/section[@class='sc-bVHCgj jYtopK']/div[@class='sc-ibQAlb sc-kMkxaj cPCcfw lkWPVq']/div[@class='sc-cFShuL bzYroq']/div[@class='pincode-input-container']/input[{l}]"))).send_keys("1")
        time.sleep(10)
        for m in range(1, 5):
            WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//body//div[@id='__next']//div[@class='sc-ibQAlb sc-kMkxaj cPCcfw lkWPVq']//div//div[@class='sc-cFShuL bzYroq']//input[{m}]"))).send_keys("1")
        time.sleep(10)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Continue']"))).click()
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "companyName"))).send_keys("Sakiba")
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Continue']"))).click()
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "To pay freelancers"))).click()
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Continue']"))).click()
        time.sleep(10)
        try:
            element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Back Up Now']")))
            
            element.click()
            
            signup_successful = True
        except TimeoutException:
            signup_successful = False
            print("SignUp Not Successful")

        self.assertTrue(signup_successful, "Signup Sucussful")

        time.sleep(10)
    def ManageProfile(self, driver):
        time.sleep(10)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Account')]"))).click()
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "name"))).send_keys("Sakiba")
        time.sleep(10)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Save changes']"))).click()
        time.sleep(5)
        name_input = driver.find_element(By.ID, "name")

        # Get the value of the input field
        input_value = name_input.get_attribute("value")

        # Check if the input value contains "Sakiba"
        if "Sakiba" in input_value:
            print("Save Successfully")
        else:
            print("save Not Successful")
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//section[@class='sc-JmfEB jSOPvM']"))).click()
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//p[@class='sc-bikFhf dtrdVx']"))).click()
        time.sleep(5)

    def logWithOTP(self, driver, otp):
        otp_digits = list(otp)  # Convert OTP string to a list of digits
        j=1
        for i, digit in enumerate(otp_digits):
            # print(digit)
            # print(j)
        
            WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, f"//div[@class='pincode-input-container']//input[{j}]"))).send_keys(digit)
            j=  j+1
            #print(digit)
            time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='Wind_App_Reports'))
