from config.config import CODE_EXPIRY_TIME
from db.models.models import verification_code
from db.repository.base_repository import BaseRepository
from datetime import datetime, timedelta

class VerificationCodeRepository(BaseRepository):
    def create_verification_code(self, user_id, code, is_used=False):
        item = verification_code(user_id, code, is_used)
        return self.put_item(item)
    
    def get_valid_verification_code(self, user_id, code):
        pk = f"USER#{user_id}"
        sk = f"CODE#{code}"
        item = self.get_item(pk, sk)
        
        if item:
            current_time = datetime.now()
            creation_time = datetime.fromisoformat(item['CreationDateTime'])
            expiry_time = creation_time + timedelta(seconds=int(CODE_EXPIRY_TIME))
            
            if current_time <= expiry_time and not item['IsUsed']:
                return item
        
        return None
    
    def update_code_to_used(self, user_id, code):
        pk = f"USER#{user_id}"
        sk = f"CODE#{code}"
        update_expression = "SET IsUsed = :val"
        expression_attribute_values = {":val": True}
        return self.update_item(pk, sk, update_expression, expression_attribute_values)