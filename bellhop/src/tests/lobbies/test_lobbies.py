from unittest.mock import MagicMock

import pytest
from core import actions, payloads
from mypy_boto3_dynamodb import DynamoDBClient
from tests import utils


class TestManageLobby:
    """
    Tests for creating & closing lobbies
    """

    def test_start_lobby(
        self,
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

        expected_event_response = payloads.generate_lobby_started_event(
            created_lobby_id
        )
        management_api_client.post_to_connection.assert_called_once_with(
            ConnectionId=connection_id, Data=expected_event_response
        )

    def test_start_lobby_custom_name(
        self, dynamo_client: DynamoDBClient, management_api_client: MagicMock
    ):
        """
        Test that starting a lobby with a custom name sets the connection as a host and sends a 'lobby started' event
        back to the host.
        """
        connection_id = "myConnection"
        custom_lobby_id = "custom_lobby_id"
        actions.add_connection(connection_id)
        created_lobby_id = actions.start_lobby(
            connection_id, management_api_client, lobby_id=custom_lobby_id
        )

        assert created_lobby_id == custom_lobby_id
        items = utils.get_all_dynamo_items(dynamo_client)
        assert items[0]["lobbyId"]["S"] == created_lobby_id

        expected_event_response = payloads.generate_lobby_started_event(
            created_lobby_id
        )
        management_api_client.post_to_connection.assert_called_once_with(
            ConnectionId=connection_id, Data=expected_event_response
        )

    def test_start_lobby_existing_name(
        self, dynamo_client: DynamoDBClient, management_api_client: MagicMock
    ):
        """
        Test that starting a lobby with a name that already exists fails
        """
        connection_id_a = "myConnectionA"
        connection_id_b = "myConnectionB"
        custom_lobby_id = "custom_lobby_id"
        actions.add_connection(connection_id_a)
        actions.add_connection(connection_id_b)
        created_lobby_id = actions.start_lobby(
            connection_id_a, management_api_client, lobby_id=custom_lobby_id
        )

        expected_success_event = payloads.generate_lobby_started_event(custom_lobby_id)
        management_api_client.post_to_connection.assert_called_with(
            ConnectionId=connection_id_a, Data=expected_success_event
        )

        # try for a second time
        second_created_lobby_id = actions.start_lobby(
            connection_id_b, management_api_client, lobby_id=custom_lobby_id
        )
        assert second_created_lobby_id is None

        expected_failure_event = payloads.generate_lobby_creation_failed_event(
            f"Lobby {custom_lobby_id} already exists."
        )
        management_api_client.post_to_connection.assert_called_with(
            ConnectionId=connection_id_b, Data=expected_failure_event
        )

    def test_close_lobby(
        self,
        dynamo_client: DynamoDBClient,
        management_api_client: MagicMock,
    ):
        """
        Test that closing a lobby removes the lobby ID and host status from the connection.
        """
        connection_id = "myConnection"
        actions.add_connection(connection_id)
        created_lobby_id = actions.start_lobby(connection_id, management_api_client)

        items = utils.get_all_dynamo_items(dynamo_client)
        assert len(items) == 1
        assert items[0]["lobbyId"]["S"] == created_lobby_id
        assert items[0]["isHost"]["BOOL"]

        actions.close_lobby(connection_id)
        items = utils.get_all_dynamo_items(dynamo_client)
        assert len(items) == 1
        assert "lobbyId" not in items[0]
        assert "isHost" not in items[0]


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
        assert created_lobby_id

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
        actions.request_join_lobby(
            "connection", "nonexistant_lobby", management_api_client
        )

        expected_reject_event = payloads.generate_join_request_rejected_event(
            "Lobby 'nonexistant_lobby' not found."
        )
        management_api_client.post_to_connection.assert_called_with(
            ConnectionId="connection", Data=expected_reject_event
        )

    def test_join_lobby_no_host(
        self,
        dynamo_client: DynamoDBClient,
        management_api_client: MagicMock,
    ):
        host_connection = "hostConnection"
        actions.add_connection(host_connection)
        lobby_id = actions.start_lobby(host_connection, management_api_client)
        assert lobby_id

        actions.request_join_lobby("guestConnection", lobby_id, management_api_client)
        actions.remove_connection(host_connection)
        actions.request_join_lobby("guestConnection2", lobby_id, management_api_client)

        expected_reject_event = payloads.generate_join_request_rejected_event(
            f"No host found for lobby '{lobby_id}'."
        )
        management_api_client.post_to_connection.assert_called_with(
            ConnectionId="guestConnection2", Data=expected_reject_event
        )


class TestJoinRequestResponses:
    def test_accept_join_request(
        self,
        dynamo_client: DynamoDBClient,
        management_api_client: MagicMock,
    ):
        """
        Test that accepting a join request sends a 'join request accepted' event to the player
        attempting to connect.
        """
        host_connection = "hostConnection"
        actions.start_lobby(host_connection, management_api_client)

        player_connection = "playerConnection"
        peer_id = 2
        actions.accept_join_request(
            player_connection_id=player_connection,
            host_connection_id=host_connection,
            peer_id=peer_id,
            management_api_client=management_api_client,
        )

        expected_accept_event = payloads.generate_join_request_accepted_event(
            host_connection, peer_id
        )
        management_api_client.post_to_connection.assert_called_with(
            ConnectionId=player_connection, Data=expected_accept_event
        )

    def test_reject_join_request(
        self,
        dynamo_client: DynamoDBClient,
        management_api_client: MagicMock,
    ):
        """
        Test that rejecting a join request sends a 'join request rejected' event to the player
        attempting to connect.
        """
        host_connection = "hostConnection"
        actions.start_lobby(host_connection, management_api_client)

        player_connection = "playerConnection"
        reason = "because I can"
        actions.reject_join_request(
            player_connection_id=player_connection,
            reason="because I can",
            management_api_client=management_api_client,
        )

        expected_reject_event = payloads.generate_join_request_rejected_event(reason)
        management_api_client.post_to_connection.assert_called_with(
            ConnectionId=player_connection, Data=expected_reject_event
        )
