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


def close_lobby(
    connection_id: str,
) -> None:
    """
    Closes the lobby for the given connection ID.
    """
    dynamo_db = get_db()

    dynamo_db.update_item(
        TableName=TABLE_NAME,
        Key={"connectionId": {"S": connection_id}},
        UpdateExpression=f"REMOVE lobbyId, isHost",
    )


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


def accept_join_request(
    player_connection_id: str,
    host_connection_id: str,
    peer_id: int,
    management_api_client,
) -> None:
    """
    Accepts a join request from a player.
    """
    event_data = payloads.generate_join_request_accepted_event(
        host_connection_id=host_connection_id, peer_id=peer_id
    )
    management_api_client.post_to_connection(
        ConnectionId=player_connection_id,
        Data=event_data,
    )


def reject_join_request(
    player_connection_id: str,
    host_connection_id: str,
    reason: str,
    management_api_client,
) -> None:
    """
    Rejects a join request from a player.
    """
    event_data = payloads.generate_join_request_rejected_event(
        host_connection_id=host_connection_id, reason=reason
    )
    management_api_client.post_to_connection(
        ConnectionId=player_connection_id,
        Data=event_data,
    )


def send_session_description(
    source_connection_id: str,
    target_connection_id: str,
    session_type: str,
    sdp: str,
    management_api_client,
) -> None:
    """
    Sends a session description to a connection.
    """
    event_data = payloads.generate_received_session_description_event(
        connection_id=source_connection_id,
        session_type=session_type,
        sdp=sdp,
    )
    management_api_client.post_to_connection(
        ConnectionId=target_connection_id,
        Data=event_data,
    )


def send_ice_candidate(
    source_connection_id: str,
    target_connection_id: str,
    media: str,
    index: int,
    name: str,
    management_api_client,
) -> None:
    """
    Sends an ice candidate to a connection.
    """
    event_data = payloads.generate_received_ice_candidate_event(
        connection_id=source_connection_id,
        media=media,
        index=index,
        name=name,
    )
    management_api_client.post_to_connection(
        ConnectionId=target_connection_id,
        Data=event_data,
    )
