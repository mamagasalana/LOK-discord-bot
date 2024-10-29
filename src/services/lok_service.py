import datetime
import requests
import urllib.parse
import logging
from config.config import DYNAMO_DB_NAME, USER, PASSWORD, LOGIN_URL, MAIL_URL
import pytz
from db.repository.user_personal_info_repository import UserPersonalInfoRepository
from db.repository.user_game_info_repository import UserGameInfoRepository
import base64
import json

class LokService:
    def __init__(self):
        self.session = requests.Session()
        self.accessToken = None
        self.codes2discord = {}  # this maps confirmation code to discord user
        self.codes2LOK = {}  # this maps confirmation code to LOK user
        self.user_game_info_repo = UserGameInfoRepository(DYNAMO_DB_NAME)
        self.user_personal_info_repo = UserPersonalInfoRepository(DYNAMO_DB_NAME)
        self.login()
        
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

        self.accessToken = response.json().get("token")
        if not self.accessToken:
            logging.error("Token not found in the response: %s", response.json())
            raise ValueError("Token not found")

    @property
    def headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Access-Token": self.accessToken,
        }
    
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

    def decryption(self, encrypted_text):
        ret = base64.b64decode(encrypted_text)
        decryption_key= [46, 101, 48, 120, 57, 49, 55, 97, 98, 51, 57, 49, 97, 50, 46]

        decryption_key_length =len(decryption_key)
        idx = 0
        out= []

        for value1 in ret:
            tmp = idx % decryption_key_length
            result = value1 ^ decryption_key[tmp]
            idx += 1
            out.append(result)

        return json.loads(bytes(out))

    def get_kingdomid_by_xy(self):
        pass

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
