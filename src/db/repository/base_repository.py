import boto3
from botocore.exceptions import ClientError
import logging

from src.config.config import AWS_ACCESS_KEY, AWS_REGION, AWS_SECRET_ACCESS_KEY

def get_dynamodb_resource():
    """Initialize and return a DynamoDB resource configured with the specified region."""
    return boto3.resource(
        "dynamodb",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

class BaseRepository:
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
        
    def update_item(self, pk, sk, update_expression, expression_attribute_values):
        """Updates an item in DynamoDB and returns the response, or None on failure."""
        try:
            response = self.table.update_item(
                Key={'PK': pk, 'SK': sk},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            logging.info(f"Successfully updated item with PK={pk}, SK={sk}")
            return response
        except ClientError as e:
            logging.error(f"Failed to update item: {e.response['Error']['Message']}")
            return None
        
    def get_item(self, pk, sk):
        """Retrieves an item from DynamoDB by primary key and sort key."""
        try:
            response = self.table.get_item(Key={'PK': pk, 'SK': sk})
            return response.get('Item')
        except ClientError as e:
            logging.error(f"Failed to get item: {e.response['Error']['Message']}")
            return None

    def delete_item(self, pk, sk):
        """Deletes an item from DynamoDB by primary key and sort key."""
        try:
            response = self.table.delete_item(Key={'PK': pk, 'SK': sk})
            logging.info(f"Successfully deleted item with PK={pk}, SK={sk}")
            return response
        except ClientError as e:
            logging.error(f"Failed to delete item: {e.response['Error']['Message']}")
            return None
