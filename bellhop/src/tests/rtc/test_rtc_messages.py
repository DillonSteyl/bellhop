from unittest.mock import MagicMock

import pytest
from core import actions, payloads
from mypy_boto3_dynamodb import DynamoDBClient
from tests import utils


def test_send_session_description(
    management_api_client: MagicMock,
):
    """
    Test that sending a session description sends the description to the target connection.
    """
    source_connection = "source_connection_id"
    target_connection = "target_connection_id"
    session_type = "session_type"
    sdp = "sdp"

    actions.send_session_description(
        source_connection_id=source_connection,
        target_connection_id=target_connection,
        session_type=session_type,
        sdp=sdp,
        management_api_client=management_api_client,
    )

    management_api_client.post_to_connection.assert_called_once_with(
        ConnectionId=target_connection,
        Data=payloads.generate_received_session_description_event(
            connection_id=source_connection,
            session_type=session_type,
            sdp=sdp,
        ),
    )


def test_send_ice_candidate(
    management_api_client: MagicMock,
):
    """
    Test that sending an ICE candidate sends the candidate to the target connection.
    """
    source_connection = "source_connection_id"
    target_connection = "target_connection_id"
    media = "media"
    index = 0
    name = "name"

    actions.send_ice_candidate(
        source_connection_id=source_connection,
        target_connection_id=target_connection,
        media=media,
        index=index,
        name=name,
        management_api_client=management_api_client,
    )

    management_api_client.post_to_connection.assert_called_once_with(
        ConnectionId=target_connection,
        Data=payloads.generate_received_ice_candidate_event(
            connection_id=source_connection,
            media=media,
            index=index,
            name=name,
        ),
    )
