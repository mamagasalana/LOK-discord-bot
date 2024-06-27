
import os
import logging
from discord_bot.bot.bot import LOKBOT
from discord_bot.config.config import CHANNEL_ID, TOKEN

def main():
    # Check if the logs directory exists, if not, create it
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure logging
    logging.basicConfig(
        filename='logs/bot.log', 
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Log the start of the bot
    logging.info('Starting LOK Discord Bot')
    
    # Initialize and start the bot
    lok_bot = LOKBOT()
    lok_bot.discord_bot(TOKEN, CHANNEL_ID)

if __name__ == '__main__':
    main()
