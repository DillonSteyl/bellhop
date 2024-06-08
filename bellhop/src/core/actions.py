import json
import uuid

from core.payloads import EventType, generate_lobby_started_event
from mypy_boto3_apigatewaymanagementapi import ApiGatewayManagementApiClient

from .services import TABLE_NAME, get_db


def add_connection(connection_id: str) -> None:
    get_db().put_item(
        TableName=TABLE_NAME,
        Item={"connectionId": {"S": connection_id}},
    )


def remove_connection(connection_id: str) -> None:
    get_db().delete_item(
        TableName=TABLE_NAME,
        Key={"connectionId": {"S": connection_id}},
    )


def start_lobby(
    connection_id: str,
    management_api_client: ApiGatewayManagementApiClient,
) -> None:
    """
    Sets the given connection as a lobby host.
    Triggers a message to the host with the created lobby ID.
    """
    lobby_id = str(uuid.uuid4())
    get_db().update_item(
        TableName=TABLE_NAME,
        Key={"connectionId": {"S": connection_id}},
        UpdateExpression=f"SET lobbyId = :lobby_id, isHost = :is_host",
        ExpressionAttributeValues={
            ":lobby_id": {"S": lobby_id},
            ":is_host": {"BOOL": True},
        },
    )

    response_data = generate_lobby_started_event(lobby_id)
    management_api_client.post_to_connection(
        ConnectionId=connection_id,
        Data=response_data,
    )
