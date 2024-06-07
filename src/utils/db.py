import os
import boto3

TABLE_NAME = os.environ.get("TABLE_NAME")


def get_db():
    return boto3.client("dynamodb")
