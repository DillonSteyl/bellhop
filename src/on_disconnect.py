import boto3
import os

TABLE_NAME = os.environ.get("TABLE_NAME")

dynamodb_client = boto3.client('dynamodb')


def lambda_handler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    dynamodb_client.delete_item(
        TableName=TABLE_NAME,
        Key={"connectionId": {"S": connection_id}}
    )

    return {
        'statusCode': 200,
    }
