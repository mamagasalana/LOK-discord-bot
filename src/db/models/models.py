from datetime import datetime

def user_personal_info(user_id, username, is_verified=False):
    current_time = datetime.now().isoformat()
    return {
        'PK': f"USER#{user_id}",
        'SK': 'PERSONAL#INFO',
        'Username': username,
        'IsVerified': is_verified,
        'CreationDateTime': current_time
    }

def user_discord_interaction(user_id, interaction_info):
    return {
        'PK': f"USER#{user_id}",
        'SK': 'DISCORD#INTERACTION',
        'InteractionInfo': interaction_info
    }

def user_game_info(user_id, user_game_id, username, world_id):
    current_time = datetime.now().isoformat()
    return {
        'PK': f"USER#{user_id}",
        'SK': f"GAME#{world_id}#{current_time}",
        'UserGameId': user_game_id,
        'Username': username,
        'WorldId': world_id,
        'CreationDateTime': current_time
    }

def verification_code(user_id, code, is_used=False):
    return {
        'PK': f"USER#{user_id}",
        'SK': f"CODE#{code}",
        'IsUsed': is_used,
        'CreationDateTime': datetime.now().isoformat()
    }
