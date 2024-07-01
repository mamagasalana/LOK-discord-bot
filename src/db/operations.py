import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('YourTableName')

def put_item(item):
    try:
        response = table.put_item(Item=item)
        return response
    except ClientError as e:
        print(f"Failed to put item: {e.response['Error']['Message']}")
        return None

def update_verification_code_status(user_id, code, is_used):
    try:
        response = table.update_item(
            Key={
                'PK': f"USER#{user_id}",
                'SK': f"CODE#{code}"
            },
            UpdateExpression="SET IsUsed = :u",
            ExpressionAttributeValues={
                ':u': is_used
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    except ClientError as e:
        print(f"Failed to update item: {e.response['Error']['Message']}")
        return None

def create_verification_code(user_id, code, is_used=False):
    return {
        'PK': f"USER#{user_id}",
        'SK': f"CODE#{code}",
        'IsUsed': is_used,
        'CreationDateTime': datetime.now().isoformat()
    }

def get_verification_code(user_id, code):
    try:
        response = table.get_item(
            Key={
                'PK': f"USER#{user_id}",
                'SK': f"CODE#{code}"
            }
        )
        return response.get('Item')
    except ClientError as e:
        print(f"Failed to get item: {e.response['Error']['Message']}")
        return None

def create_user_game_info(user_id, user_game_id, username, world_id):
    return {
        'PK': f"USER#{user_id}",
        'SK': f"GAME#{user_game_id}",
        'Username': username,
        'WorldId': world_id,
        'CreationDateTime': datetime.now().isoformat()
    }

def store_user_game_info(user_id, user_game_id, username, world_id):
    item = create_user_game_info(user_id, user_game_id, username, world_id)
    return put_item(item)
