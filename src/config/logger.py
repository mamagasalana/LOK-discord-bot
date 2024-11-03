import os
import logging


def setup_logger(name, log_file, level=logging.INFO):
    """Sets up a logger with a specific name, log file, and logging level."""
    # Create the logger with the given name
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a file handler for writing logs to the specified file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Define the format for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    if not logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.propagate = False
    
    return logger


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
    setup_logger("wss", "logs/wss.log", level=logging.DEBUG)