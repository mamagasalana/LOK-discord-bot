from db.models.models import user_discord_interaction
from db.repository.base_repository import BaseRepository

class UserDiscordInteractionRepository(BaseRepository):
    def create_user_discord_interaction(self, user_id, interaction_info):
        item = user_discord_interaction(user_id, interaction_info)
        return self.put_item(item)
    
    def get_user_discord_interaction(self, user_id):
        pk = f"USER#{user_id}"
        sk = 'DISCORD#INTERACTION'
        return self.get_item(pk, sk)
    
    def delete_user_discord_interaction(self, user_id):
        pk = f"USER#{user_id}"
        sk = 'DISCORD#INTERACTION'
        return self.delete_item(pk, sk)
