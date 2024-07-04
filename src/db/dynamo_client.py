import boto3
from botocore.exceptions import ClientError
from src.config.config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION, DYNAMO_DB_NAME

# Configure the boto3 resource with AWS credentials
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def create_table():
    table_name = DYNAMO_DB_NAME
    try:
        # Check if table already exists
        table = dynamodb.Table(table_name)
        table.load()  # This will raise an error if the table does not exist
        print(f"Table {table_name} already exists.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            # Table does not exist, create it
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "primaryKey", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "primaryKey", "AttributeType": "S"},
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
            print(f"Table {table_name} created successfully.")
        else:
            # Handle other exceptions
            print(f"Unexpected error: {e}")
            raise

if __name__ == "__main__":
    create_table()
