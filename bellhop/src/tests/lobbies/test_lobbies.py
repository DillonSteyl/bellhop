import json
from unittest.mock import MagicMock

import pytest
from core import payloads, actions
from mypy_boto3_dynamodb import DynamoDBClient
from tests import utils


def test_start_lobby(
    dynamo_client: DynamoDBClient,
    management_api_client: MagicMock,
):
    """
    Test that starting a lobby sets the connection as a host and sends a 'lobby started' event
    back to the host.
    """
    connection_id = "myConnection"

    actions.add_connection(connection_id)
    items = utils.get_all_dynamo_items(dynamo_client)
    assert len(items) == 1
    assert items[0]["connectionId"]["S"] == connection_id
    assert items[0].get("lobbyId") is None

    actions.start_lobby(connection_id, management_api_client)
    items = utils.get_all_dynamo_items(dynamo_client)
    assert len(items) == 1
    created_lobby_id = items[0]["lobbyId"]["S"]
    assert created_lobby_id is not None
    assert items[0].get("isHost")

    expected_event_response = payloads.generate_lobby_started_event(created_lobby_id)
    management_api_client.post_to_connection.assert_called_once_with(
        ConnectionId=connection_id, Data=expected_event_response
    )
