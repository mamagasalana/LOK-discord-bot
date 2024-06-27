import requests
import urllib.parse

from ..bot.commands import VerifyButton
from ..config.config import USER, PASSWORD, LOGIN_URL, MAIL_URL
import discord
from discord.ext import commands, tasks

from discord.ui import View

class LOKBOT:
    def __init__(self):
        self.session = requests.Session()
        self.xtoken = None
        self.codes2discord = {}
        self.codes2LOK = {}
        self.button = None

    async def get_id(self, verification_code):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        if self.xtoken is None:
            payload = '{"authType":"email","email":"%s","password":"%s"}' % (USER, PASSWORD)
            encoded_payload = 'json=' + urllib.parse.quote(payload)
            r = self.session.post(LOGIN_URL, headers=headers, data=encoded_payload)
            if r.status_code == 200:
                self.xtoken = r.json().get('token')
                if self.xtoken is None:
                    print("Token not found in the response:", r.json())
                    return  # Exit if no token is found
            else:
                print("Failed to login, status code:", r.status_code)
                return  # Exit on failed login attempt

        headers['X-Access-Token'] = self.xtoken
        payload = '{"category":5}'
        encoded_payload = 'json=' + urllib.parse.quote(payload)
        r = self.session.post(MAIL_URL, headers=headers, data=encoded_payload)
        mailist = r.json()['mails']

        for mail in mailist:
            uid = mail['_id']
            username = mail['from']['name']
            subject = mail['subject']['subject']
            if subject == verification_code:
                self.codes2LOK[verification_code] = [username, uid]

    def discord_bot(self, token, channel_id):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        bot = commands.Bot(command_prefix='!', intents=intents)

        @bot.event
        async def on_ready():
            channel = await bot.fetch_channel(channel_id)
            if channel:
                await channel.send("Bot has joined the channel!")
                self.button = VerifyButton()
                view = View()
                view.add_item(self.button)
                await channel.send("Click the button to get your verification code:", view=view)
                self.check_time.start()
            else:
                print(f"Channel with ID {channel_id} not found.")

        @tasks.loop(minutes=1)
        async def check_time():
            self.codes2discord.update(self.button.codes)
            for verification_code in self.codes2discord:
                if verification_code not in self.codes2LOK:
                    await self.get_id(verification_code)

        self.check_time = check_time
        bot.run(token)

if __name__ == '__main__':
    from src.discord_bot.config.config import TOKEN, CHANNEL_ID
    lok_bot = LOKBOT()
    lok_bot.discord_bot(TOKEN, CHANNEL_ID)
