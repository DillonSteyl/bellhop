from core.services import TABLE_NAME
from mypy_boto3_dynamodb import DynamoDBClient


def get_all_dynamo_items(db_client: DynamoDBClient) -> list[dict]:
    scanner = db_client.get_paginator("scan")
    iterator = scanner.paginate(TableName=TABLE_NAME)
    items = []
    for i in iterator:
        items.extend(i["Items"])
    return items


def clear_db(db_client: DynamoDBClient) -> None:
    for item in get_all_dynamo_items(db_client):
        db_client.delete_item(
            TableName=TABLE_NAME, Key={"connectionId": {"S": item["connectionId"]["S"]}}
        )
