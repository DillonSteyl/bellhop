import uuid

from core import payloads

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
    management_api_client,
) -> str:
    """
    Sets the given connection as a lobby host.
    Triggers a message to the host with the created lobby ID.

    Returns the lobby ID.
    """
    dynamo_db = get_db()

    lobby_id = str(uuid.uuid4())
    dynamo_db.update_item(
        TableName=TABLE_NAME,
        Key={"connectionId": {"S": connection_id}},
        UpdateExpression=f"SET lobbyId = :lobby_id, isHost = :is_host",
        ExpressionAttributeValues={
            ":lobby_id": {"S": lobby_id},
            ":is_host": {"BOOL": True},
        },
    )

    response_data = payloads.generate_lobby_started_event(lobby_id)

    management_api_client.post_to_connection(
        ConnectionId=connection_id,
        Data=response_data,
    )
    return lobby_id


def request_join_lobby(
    connection_id: str,
    lobby_id: str,
    management_api_client,
) -> None:
    """
    Request to join a lobby based on the given lobby ID.
    """
    dynamo_db = get_db()

    lobby_connections = dynamo_db.query(
        TableName=TABLE_NAME,
        IndexName="lobbyIndex",
        KeyConditionExpression="lobbyId = :lobby_id",
        ExpressionAttributeValues={":lobby_id": {"S": lobby_id}},
    )
    if not lobby_connections:
        raise RuntimeError(f"Lobby {lobby_id} not found.")

    host_id = None
    for item in lobby_connections["Items"]:
        isHost = item.get("isHost", {}).get("BOOL", False)
        if isHost:
            host_id = item["connectionId"]["S"]

    if not host_id:
        raise RuntimeError(f"No host found for lobby {lobby_id}.")

    dynamo_db.update_item(
        TableName=TABLE_NAME,
        Key={"connectionId": {"S": connection_id}},
        UpdateExpression=f"SET lobbyId = :lobby_id, isHost = :is_host",
        ExpressionAttributeValues={
            ":lobby_id": {"S": lobby_id},
            ":is_host": {"BOOL": False},
        },
    )

    event_data = payloads.generate_received_join_request_event(connection_id)
    management_api_client.post_to_connection(
        ConnectionId=host_id,
        Data=event_data,
    )
