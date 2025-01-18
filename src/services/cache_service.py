import json
import os

MESSAGE_ID_FILE = 'src/cache/main_message_id.json'
USER_RESOURCE_SELECTION_CACHE_FILE = 'src/cache/user_resource_selection_cache.json'

class BOT_CACHE:
    @staticmethod
    def save_message_id(message_id):
        with open(MESSAGE_ID_FILE, 'w') as f:
            json.dump({"message_id": message_id}, f)

    @staticmethod
    def load_message_id():
        if not os.path.exists(MESSAGE_ID_FILE):
            return None
        with open(MESSAGE_ID_FILE, 'r') as f:
            data = json.load(f)
            return data.get("message_id")
        
    @staticmethod
    def save_user_selection(js):
        with open(USER_RESOURCE_SELECTION_CACHE_FILE, 'w') as f:
            json.dump(js, f)

    @staticmethod
    def load_user_selection():
        if not os.path.exists(USER_RESOURCE_SELECTION_CACHE_FILE):
            return {}
        with open(USER_RESOURCE_SELECTION_CACHE_FILE, 'r') as f:
            data = json.load(f)
            return data