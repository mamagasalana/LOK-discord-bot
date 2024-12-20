import requests
from services.crypto_service import crypto
from services.wss_service import LOKWSS
import os
import logging
import json
import urllib.parse
from config.config import LOGIN_URL, MAIL_URL
from db.repository.user_personal_info_repository import UserPersonalInfoRepository
from db.repository.user_game_info_repository import UserGameInfoRepository
from config.config import DYNAMO_DB_NAME
import asyncio
import datetime

class LokService:
    def __init__(self, user, password, botname, rest_hour):
        self.USER  =user
        self.PASSWORD  =password
        self.CACHED_LOGIN = f"{botname}.json"
        self.crypto = crypto()
        self.wss = LOKWSS(self.crypto, logger_name=botname)
        self.session = None
        self.accessToken = None
        self.rest_hour = rest_hour
        self.status = 1  # to check if bot got banned
        self.init = False
        if not self.resting:
            print(f"{botname} has started to work")
            self.relogin()
        else:
            print(f"{botname} still sleeping")

        self.codes2discord = {}  # this maps confirmation code to discord user
        self.codes2LOK = {}  # this maps confirmation code to LOK user
        self.user_game_info_repo = UserGameInfoRepository(DYNAMO_DB_NAME)
        self.user_personal_info_repo = UserPersonalInfoRepository(DYNAMO_DB_NAME)

    @property
    def resting(self):
        now = datetime.datetime.now()
        start = now.replace(hour=self.rest_hour, minute=0, second=0, microsecond=0)
        end  = start + datetime.timedelta(hours=8)
        ret =  start <= now <= end
        if ret:
            self.init = False
        
        return ret
        

    async def start_wss(self):
        if self.status == 0: # Check if account got banned
            return
        
        if not self.init:
            self.relogin()

        SUCCESS =False
        for _ in range(3):
            SUCCESS = await self.wss.main()
            if SUCCESS:
                break
            self.relogin(force=True)
            await asyncio.sleep(5)

        if not SUCCESS:
            self.status= 0

    @property
    def headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Access-Token": self.accessToken,
        }

    def relogin(self, force=False):
        """
        Reuse access token to reduce spamming 
        """
        self.session = requests.Session() # open a new session
        if not os.path.exists(self.CACHED_LOGIN) or force:
            self.login()

        js = json.load(open(self.CACHED_LOGIN))
        self.accessToken = js.get("token")
        if not self.accessToken:
            logging.error("Token not found in the response: %s", js)
            raise ValueError("Token not found")
        regionHash = js.get("regionHash")

        self.crypto.update_salt(regionHash)
        self.crypto.update_token(self.accessToken)
        #validate if salt works
        url = 'https://api-lok-live.leagueofkingdoms.com/api/kingdom/task/all'
        data = {'json': self.crypto.encryption('{}')}
        r = self.session.post(url, headers=self.headers, data=data)
        
        if not r.content.startswith(b'V'):
            os.remove(self.CACHED_LOGIN)
            return self.relogin()
        else:
            js = self.crypto.decryption(r.content)
            if 'err' in js:
                if js['err'].get('code') == 'no_auth':
                    os.remove(self.CACHED_LOGIN)
                    return self.relogin()

        self.init=True

    # login api to get access token
    def login(self):
        payload = (
            '{"authType":"email","email":"%s","password":"%s","deviceInfo":{"build":"global","OS":"Windows 10","country":"USA","language":"English","bundle":"","version":"1.1775.158.242","platform":"web","pushId":""}}'
            % (self.USER, self.PASSWORD)
        )
        encoded_payload = "json=" + urllib.parse.quote(payload)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = self.session.post(LOGIN_URL, headers=headers, data=encoded_payload)
        response.raise_for_status()
        with open(self.CACHED_LOGIN, 'w') as ofile:
            ofile.write(json.dumps(response.json()))

    # get personal email list
    def get_personal_email_list(self):
        payload = '{"category":0}'
        encoded_payload = "json=" + urllib.parse.quote(payload)
        response = self.session.post(MAIL_URL, headers=self.headers, data=encoded_payload)
        response.raise_for_status()

        mails = response.json().get("mails", [])

        if not mails:
            logging.error("Mail not found, something changed in MAIL_URL?")
            return []
        return mails
    
        # Current time in UTC
        now_utc = datetime.datetime.now(pytz.utc)

        # Filter emails received within the last 30 seconds
        filtered_mails = [
            mail
            for mail in mails
            if datetime.datetime.strptime(
                mail["receiveDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).replace(tzinfo=pytz.utc)
            > now_utc - datetime.timedelta(seconds=30)
        ]

        return filtered_mails

    def get_title(self):
        url = 'https://api-lok-live.leagueofkingdoms.com/api/shrine/title'
        payload = '{}'
        encoded_payload = "json=" + urllib.parse.quote(payload)
        response = self.session.post(url, headers=self.headers, data=encoded_payload)
        response.raise_for_status()

        return response.json().get("titles")
    
    def set_title(self, kingdomid, title):
        TITLES = self.get_title()
        # kingdomid= self.get_kingdomid_by_xy(x, y)
        url = 'https://api-lok-live.leagueofkingdoms.com/api/shrine/title/change'
        code =1
        payload = '{"code":%s,"targetKingdomId":"%s"}' % (code, kingdomid)
        encoded_payload = "json=" + urllib.parse.quote(payload)
        response = self.session.post(url, headers=self.headers, data=encoded_payload)
        response.raise_for_status()
        
    async def get_verification_code_from_mail(self):
        """Fetch user IDs from the external service."""
        if not self.accessToken:
            # If no token, attempt to login
            try:
                self.login()
            except Exception as e:
                logging.error("Failed to login: %s", e)
                return

        # Fetch emails from the external service
        mails = self.get_personal_email_list()
        for mail in mails:
            user_id = mail["_id"]
            username = mail["from"]["name"]
            world_id = mail["from"]["worldId"]
            subject = mail["subject"]["subject"]
            content = mail["content"]

            # Verify the code
            code_item = self.context.get_verification_code(user_id, subject)
            if code_item:
                print(f"Verification code {subject} found for user {code_item['PK']}")
                # Add logic here if you want to update the verification status in DynamoDB

            # Store the email subject and content with the code
            if subject not in self.codes2LOK:
                self.codes2LOK[subject] = content

                # Store user game info
                self.context.store_user_game_info(user_id, username, world_id)
