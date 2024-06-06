import os
import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "WebsocketConnections")
DEPLOYED_ENVIRONMENT = os.environ.get("DEPLOYED_ENVIRONMENT", "local")


def get_db():
    if DEPLOYED_ENVIRONMENT == "local":
        return boto3.client(
            "dynamodb",
            endpoint_url="http://localstack:4566",
        )

    return boto3.client("dynamodb")
