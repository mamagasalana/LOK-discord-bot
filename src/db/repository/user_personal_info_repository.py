from db.models.models import user_personal_info
from db.repository.base_repository import BaseRepository

class UserPersonalInfoRepository(BaseRepository):
    def create_user_personal_info(self, user_id, username, is_verified=False):
        item = user_personal_info(user_id, username, is_verified)
        return self.put_item(item)
    
    def get_user_personal_info(self, user_id):
        pk = f"USER#{user_id}"
        sk = 'PERSONAL#INFO'
        return self.get_item(pk, sk)
