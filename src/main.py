import asyncio
import logging
from discord_bot.bot import LOKBOT
from config.config import CHANNEL_ID, TOKEN
from config.config import DYNAMO_DB_NAME
from config.logger import setup_logging
from db.repository.user_game_info_repository import UserGameInfoRepository

def display_all_game_info():
    # Create an instance of the DynamoDBManager with the correct table name
    user_personal_info_repo = UserGameInfoRepository(DYNAMO_DB_NAME)
    
    # Fetch all game info entries
    game_infos = user_personal_info_repo.get_all_users_game_info()
    
    if game_infos:
        print("Retrieved all game info entries:")
        for info in game_infos:
            print(info)
    else:
        print("No game info entries found.")
        
def main():
    # Setup logging
    setup_logging()
    logging.info("Starting LOK Discord Bot")

    # Initialize and start the bot
    lok_bot = LOKBOT()
    lok_bot.discord_bot(TOKEN, CHANNEL_ID)

    # Run this to test the DynamoDBManager
    # Uncomment the line below to test the DynamoDBManager
    # display_all_game_info()

if __name__ == "__main__":
    main()
