from datetime import datetime

def create_user_personal_info(user_id, username, is_verified=False):
    return {
        'PK': f"USER#{user_id}",
        'SK': 'PERSONAL#INFO',
        'Username': username,
        'IsVerified': is_verified
    }

def create_user_discord_interaction(user_id, interaction_info):
    return {
        'PK': f"USER#{user_id}",
        'SK': 'DISCORD#INTERACTION',
        'InteractionInfo': interaction_info
    }

def create_user_game_info(user_id, user_game_id, world_id):
    return {
        'PK': f"USER#{user_id}",
        'SK': f"GAME#{user_game_id}",
        'WorldId': world_id
    }

def create_verification_code(user_id, code, is_used=False):
    return {
        'PK': f"USER#{user_id}",
        'SK': f"CODE#{code}",
        'IsUsed': is_used,
        'CreationDateTime': datetime.now().isoformat()
    }
