import datetime
import requests
import urllib.parse
import logging
from config.config import DYNAMO_DB_NAME, USER, PASSWORD, LOGIN_URL, MAIL_URL
import pytz
import json
import os
import aiohttp

from db.repository.user_personal_info_repository import UserPersonalInfoRepository
from db.repository.user_game_info_repository import UserGameInfoRepository
from db.resources.mine import Mine

from services.crypto_service import crypto
from services.wss_service import LOKWSS

CACHED_LOGIN = 'login.json'

class LokService:
    def __init__(self):
        self.session = requests.Session()
        self.accessToken = None
        self.codes2discord = {}  # this maps confirmation code to discord user
        self.codes2LOK = {}  # this maps confirmation code to LOK user
        self.user_game_info_repo = UserGameInfoRepository(DYNAMO_DB_NAME)
        self.user_personal_info_repo = UserPersonalInfoRepository(DYNAMO_DB_NAME)
        self.crypto = crypto()
        self.wss = LOKWSS(self.crypto)
        self.relogin()

    def relogin(self):
        """
        Reuse access token to reduce spamming 
        """
        if not os.path.exists(CACHED_LOGIN):
            self.login()

        js = json.load(open(CACHED_LOGIN))
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
            os.remove(CACHED_LOGIN)
            self.relogin()
        else:
            js = self.crypto.decryption(r.content)
            if 'err' in js:
                if js['err'].get('code') == 'no_auth':
                    os.remove(CACHED_LOGIN)
                    self.relogin()


    # login api to get access token
    def login(self):
        payload = (
            '{"authType":"email","email":"%s","password":"%s","deviceInfo":{"build":"global","OS":"Windows 10","country":"USA","language":"English","bundle":"","version":"1.1775.158.242","platform":"web","pushId":""}}'
            % (USER, PASSWORD)
        )
        encoded_payload = "json=" + urllib.parse.quote(payload)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = self.session.post(LOGIN_URL, headers=headers, data=encoded_payload)
        response.raise_for_status()
        with open(CACHED_LOGIN, 'w') as ofile:
            ofile.write(json.dumps(response.json()))

    @property
    def headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Access-Token": self.accessToken,
        }
    
    async def get_occupied(self, foid):
        url = 'https://api-lok-live.leagueofkingdoms.com/api/field/fieldobject/info'
        payload = {"json": json.dumps({"foId": foid})}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, data=payload) as response:
                data = await response.json() 
                return data
        

    def zone_from_xy(self, x, y):
        if (2048 > x >= 0) and (2048 > y >= 0):
            return int(x/32) + int(y/32)*64
        return -1
        
    def zone_adjacent(self, zone):
        fx = lambda x: [x-64, x , x +64]
        
        if zone % 64 == 0:
            # left edge
            out = fx(zone) + fx(zone+1)
        elif zone % 63 == 0:
            # right edge
            out = fx(zone-1) + fx(zone)
        else:
            out = fx(zone-1) + fx(zone) + fx(zone+1) 
        return [x for x in out if  4096 > x >=0 ]
    
    def check_entire_map(self, start_x = 0, start_y=2048):
        #only covers top half of the map, y from 2048
        for y in range(start_y, 4096, 192):
            for x in range(start_x, 63, 3):
                self.wss.pending_task.append(self.zone_adjacent(x+y+65))

    def get_mine(self, dt, mine_id= 20100105, level=1):
        """
        crystal mine id 'fo_20100105'
        """
        r = Mine.select().where((Mine.expiry > datetime.datetime.now()) 
                                & (Mine.date > dt)
                                & (Mine.code ==mine_id)
                                & (Mine.level >=level))
        return r
    
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
