from unittest.mock import MagicMock

import pytest
from core import actions, payloads
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

    created_lobby_id = actions.start_lobby(connection_id, management_api_client)
    items = utils.get_all_dynamo_items(dynamo_client)
    assert len(items) == 1
    assert items[0]["lobbyId"]["S"] == created_lobby_id
    assert created_lobby_id is not None
    assert items[0].get("isHost")

    expected_event_response = payloads.generate_lobby_started_event(created_lobby_id)
    management_api_client.post_to_connection.assert_called_once_with(
        ConnectionId=connection_id, Data=expected_event_response
    )


class TestJoinLobby:
    def test_join_lobby(
        self,
        dynamo_client: DynamoDBClient,
        management_api_client: MagicMock,
    ):
        """
        Test that joining a lobby sets the connection as a guest and sends a 'received join request' event
        back to the host.
        """

        host_connection = "hostConnection"
        created_lobby_id = actions.start_lobby(host_connection, management_api_client)

        guest_connection = "guestConnection"
        actions.add_connection(guest_connection)
        actions.request_join_lobby(
            guest_connection, created_lobby_id, management_api_client
        )

        expected_request_join_event = payloads.generate_received_join_request_event(
            guest_connection
        )
        management_api_client.post_to_connection.assert_called_with(
            ConnectionId=host_connection, Data=expected_request_join_event
        )

    def test_join_nonexistant_lobby(
        self,
        dynamo_client: DynamoDBClient,
        management_api_client: MagicMock,
    ):
        with pytest.raises(RuntimeError):
            actions.request_join_lobby(
                "connection", "nonexistant_lobby", management_api_client
            )

    def test_join_lobby_no_host(
        self,
        dynamo_client: DynamoDBClient,
        management_api_client: MagicMock,
    ):
        host_connection = "hostConnection"
        actions.add_connection(host_connection)
        lobby_id = actions.start_lobby(host_connection, management_api_client)

        actions.request_join_lobby("guestConnection", lobby_id, management_api_client)
        actions.remove_connection(host_connection)
        with pytest.raises(RuntimeError):
            actions.request_join_lobby(
                "guestConnection2", lobby_id, management_api_client
            )
