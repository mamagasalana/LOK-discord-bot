# db/repository/user_game_info_repository.py
import logging
from aiohttp import ClientError
from db.repository.base_repository import BaseRepository
from db.models.models import user_game_info

class UserGameInfoRepository(BaseRepository):
    def create_user_game_info(self, user_id, user_game_id, username, world_id):
        item = user_game_info(user_id, user_game_id, username, world_id)
        return self.put_item(item)

    def get_user_game_info(self, user_id, world_id, creation_datetime):
        pk = f"USER#{user_id}"
        sk = f"GAME#{world_id}#{creation_datetime}"
        return self.get_item(pk, sk)

    def get_all_users_game_info(self):
        items = []
        last_evaluated_key = None
        
        while True:
            scan_kwargs = {
                "FilterExpression": "begins_with(SK, :prefix)",
                "ExpressionAttributeValues": {":prefix": "GAME#"}
            }

            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

            try:
                response = self.table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break
            except ClientError as e:
                logging.error(f"Failed to scan items: {e.response['Error']['Message']}")
                break
        return items
