import os
import logging


def setup_logging():
    # Check if the logs directory exists, if not, create it
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Configure logging
    logging.basicConfig(
        filename="logs/bot.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
