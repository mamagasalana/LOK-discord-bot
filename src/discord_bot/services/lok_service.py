import datetime
import requests
import urllib.parse
import logging
from ..config.config import USER, PASSWORD, LOGIN_URL, MAIL_URL
import pytz

class LokService:
    def __init__(self):
        self.session = requests.Session()
        self.accessToken = None
        self.codes2discord  = {}  # this map confirmation code to discord user
        self.codes2LOK  = {} # this map confirmation code to LOK user

    def login(self):
        payload = '{"authType":"email","email":"%s","password":"%s","deviceInfo":{"build":"global","OS":"Windows 10","country":"USA","language":"English","bundle":"","version":"1.1775.158.242","platform":"web","pushId":""}}' % (USER, PASSWORD) 
        encoded_payload = 'json=' + urllib.parse.quote(payload)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = self.session.post(LOGIN_URL, headers=headers, data=encoded_payload)
        response.raise_for_status()
        
        self.accessToken = response.json().get('token')
        if not self.accessToken:
            logging.error("Token not found in the response: %s", response.json())
            raise ValueError("Token not found")

    def fetch_emails(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Access-Token': self.accessToken,
        }
        payload = '{"category":5}'
        encoded_payload = 'json=' + urllib.parse.quote(payload)
        response = self.session.post(MAIL_URL, headers=headers, data=encoded_payload)
        response.raise_for_status()

        mails = response.json().get('mails', [])
        
        if not mails:
            logging.error('Mail not found, something changed in MAIL_URL?')
            return []

        # Current time in UTC
        now_utc = datetime.datetime.now(pytz.utc)

        # Filter emails received within the last 5 seconds
        filtered_mails = [mail for mail in mails if datetime.datetime.strptime(mail['receiveDate'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc) > now_utc - datetime.timedelta(seconds=5)]

        return filtered_mails

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
        mails = self.fetch_emails()
        for mail in mails:
            uid = mail['_id']
            username = mail['from']['name']
            subject = mail['subject']['subject']
            # Map subject to LOK user if it exists in the Discord mapping but not in LOK mapping
            if subject in self.codes2discord and subject not in self.codes2LOK:
                self.codes2LOK[subject] = [username, uid]