import os
from dotenv import load_dotenv
from typing import Optional

def load_env_variable(variable_name: str, default: Optional[str] = None) -> str:
    """Load an environment variable and handle errors if not set."""
    value = os.getenv(variable_name, default)
    if value is None:
        raise EnvironmentError(f"Environment variable '{variable_name}' is not set.")
    return value

def load_environment_variables() -> dict:
    """Load environment variables and return them as a dictionary."""
    load_dotenv()
    
    env_vars = {
        "USER": load_env_variable("USER"),
        "PASSWORD": load_env_variable("PASSWORD"),
        "LOGIN_URL": load_env_variable("LOGIN_URL"),
        "MAIL_URL": load_env_variable("MAIL_URL"),
        "TOKEN": load_env_variable("TOKEN"),
        "CHANNEL_ID": load_env_variable("CHANNEL_ID"),
        "GUILD_ID": load_env_variable("GUILD_ID"),
        "CODE_EXPIRY_TIME": load_env_variable("CODE_EXPIRY_TIME", "60"),
        "AWS_ACCESS_KEY": load_env_variable("AWS_ACCESS_KEY"),
        "AWS_SECRET_ACCESS_KEY": load_env_variable("AWS_SECRET_ACCESS_KEY"),
        "AWS_REGION": load_env_variable("AWS_REGION", "ap-southeast-1"),
        "DYNAMO_DB_NAME": load_env_variable("DYNAMO_DB_NAME"),
        "DEFAULT_WORLD" : load_env_variable("DEFAULT_WORLD")
    }
    
    return env_vars

# Load environment variables
environment_variables = load_environment_variables()

# Accessing the loaded variables
USER = environment_variables["USER"]
PASSWORD = environment_variables["PASSWORD"]
LOGIN_URL = environment_variables["LOGIN_URL"]
MAIL_URL = environment_variables["MAIL_URL"]
TOKEN = environment_variables["TOKEN"]
CHANNEL_ID = environment_variables["CHANNEL_ID"]
GUILD_ID = environment_variables["GUILD_ID"]
CODE_EXPIRY_TIME = environment_variables["CODE_EXPIRY_TIME"]
AWS_ACCESS_KEY = environment_variables["AWS_ACCESS_KEY"]
AWS_SECRET_ACCESS_KEY = environment_variables["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = environment_variables["AWS_REGION"]
DYNAMO_DB_NAME = environment_variables["DYNAMO_DB_NAME"]
DEFAULT_WORLD = environment_variables["DEFAULT_WORLD"]
