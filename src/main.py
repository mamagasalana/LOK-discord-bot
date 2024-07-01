import logging
from discord_bot.bot import LOKBOT
from config.config import CHANNEL_ID, TOKEN
from config.logger import setup_logging


def main():
    # Setup logging
    setup_logging()
    logging.info("Starting LOK Discord Bot")

    # Initialize and start the bot
    lok_bot = LOKBOT()
    lok_bot.discord_bot(TOKEN, CHANNEL_ID)


if __name__ == "__main__":
    main()
