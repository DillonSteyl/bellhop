import os
import boto3
from unittest.mock import MagicMock


TABLE_NAME = os.environ.get("TABLE_NAME", "WebsocketConnections")
DEPLOYED_ENVIRONMENT = os.environ.get("DEPLOYED_ENVIRONMENT", "local")


def get_db():
    if DEPLOYED_ENVIRONMENT == "local":
        return boto3.client(
            "dynamodb",
            endpoint_url="http://localstack:4566",
        )

    return boto3.client("dynamodb")


def get_management_api_client():
    if DEPLOYED_ENVIRONMENT == "local":
        # localstack requires pro account to deploy api gateway v2
        return MagicMock()

    return boto3.client("apigatewaymanagementapi")
