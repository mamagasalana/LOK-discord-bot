import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import logging
from config.config import AWS_ACCESS_KEY, AWS_REGION, AWS_SECRET_ACCESS_KEY

def get_dynamodb_resource():
    """Initialize and return a DynamoDB resource configured with the specified region."""
    return boto3.resource(
        "dynamodb",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

class DynamoDBManager:
    def __init__(self, table_name):
        self.dynamodb_resource = get_dynamodb_resource()
        self.table = self.dynamodb_resource.Table(table_name)

    def put_item(self, item):
        """Inserts an item into DynamoDB and returns the response, or None on failure."""
        try:
            response = self.table.put_item(Item=item)
            logging.info(f"Successfully put item: {item}")
            return response
        except ClientError as e:
            logging.error(f"Failed to put item: {e.response['Error']['Message']}")
            return None

    def create_user_game_info(self, user_id, user_game_id, username, world_id):
        """Constructs a dictionary representing a user game info item."""
        return {
            'PK': f"USER#{user_id}",
            'SK': f"GAME#{user_game_id}",
            'Username': username,
            'WorldId': world_id,
            'CreationDateTime': datetime.now().isoformat()
        }

    def store_user_game_info(self, user_id, user_game_id, username, world_id):
        """Stores user game information into DynamoDB."""
        item = self.create_user_game_info(user_id, user_game_id, username, world_id)
        return self.put_item(item)

    def get_user_game_info(self, user_id, user_game_id):
        """Retrieves user game information from DynamoDB."""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"USER#{user_id}",
                    'SK': f"GAME#{user_game_id}"
                }
            )
            return response.get('Item')
        except ClientError as e:
            logging.error(f"Failed to get item: {e.response['Error']['Message']}")
            return None

    def get_all_users_game_info(self):
        """Retrieves all game information items where the sort key starts with 'GAME#'."""
        items = []
        last_evaluated_key = None
        
        # Continuously fetch data until no more pages are available
        while True:
            scan_kwargs = {
                "FilterExpression": "begins_with(SK, :prefix)",
                "ExpressionAttributeValues": {":prefix": "GAME#"}
            }

            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

            try:
                response = self.table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))  # Add results from this page to the list
                last_evaluated_key = response.get('LastEvaluatedKey')  # Determine if there's more data
                if not last_evaluated_key:
                    break
            except ClientError as e:
                logging.error(f"Failed to scan items: {e.response['Error']['Message']}")
                break

        return items
