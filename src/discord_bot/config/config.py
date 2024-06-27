from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Global variables
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
LOGIN_URL = os.getenv("LOGIN_URL")
MAIL_URL = os.getenv("MAIL_URL")
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
