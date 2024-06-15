from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)
from aws_lambda_powertools.utilities.typing import LambdaContext
from core import payloads, actions, services


@event_source(data_class=APIGatewayProxyEvent)
def on_connect(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Handles new connections - inserting a row into DynamoDB
    """
    connection_id = event.request_context.connection_id or ""
    actions.add_connection(connection_id)
    return {}


@event_source(data_class=APIGatewayProxyEvent)
def on_disconnect(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Handles disconnections - deleting a row from DynamoDB
    """
    connection_id = event.request_context.connection_id or ""
    actions.remove_connection(connection_id)
    return {}


@event_source(data_class=APIGatewayProxyEvent)
def handle_payload(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Generic handler for websocket requests
    """
    payload = payloads.WebsocketPayload(**event.json_body)
    source_connection_id = event.request_context.connection_id or ""

    management_api_client = services.get_management_api_client(
        domain_name=event.request_context.domain_name or "",
        stage=event.request_context.stage,
    )
    content = payload.content or {}

    match payload.action:
        case payloads.ActionType.START_LOBBY:
            actions.start_lobby(
                connection_id=source_connection_id,
                management_api_client=management_api_client,
            )
        case payloads.ActionType.CLOSE_LOBBY:
            actions.close_lobby(connection_id=source_connection_id)
        case payloads.ActionType.JOIN_LOBBY:
            join_lobby_content = payloads.JoinLobbyContent(**content)
            actions.request_join_lobby(
                connection_id=source_connection_id,
                lobby_id=join_lobby_content.lobby_id,
                management_api_client=management_api_client,
            )
        case payloads.ActionType.ACCEPT_JOIN_REQUEST:
            accept_join_content = payloads.AcceptJoinRequestContent(**content)
            actions.accept_join_request(
                player_connection_id=accept_join_content.player_connection_id,
                host_connection_id=source_connection_id,
                peer_id=accept_join_content.player_peer_id,
                management_api_client=management_api_client,
            )
        case payloads.ActionType.REJECT_JOIN_REQUEST:
            reject_join_content = payloads.RejectJoinRequestContent(**content)
            actions.reject_join_request(
                player_connection_id=reject_join_content.player_connection_id,
                host_connection_id=source_connection_id,
                reason=reject_join_content.reason,
                management_api_client=management_api_client,
            )
        case payloads.ActionType.SEND_SESSION_DESCRIPTION:
            send_session_description_content = payloads.SendSessionDescriptionContent(
                **content
            )
            actions.send_session_description(
                source_connection_id=source_connection_id,
                target_connection_id=send_session_description_content.connection_id,
                session_type=send_session_description_content.session_type,
                sdp=send_session_description_content.sdp,
                management_api_client=management_api_client,
            )
        case payloads.ActionType.SEND_ICE_CANDIDATE:
            send_ice_candidate_content = payloads.SendICECandidateContent(**content)
            actions.send_ice_candidate(
                source_connection_id=source_connection_id,
                target_connection_id=send_ice_candidate_content.connection_id,
                media=send_ice_candidate_content.media,
                index=send_ice_candidate_content.index,
                name=send_ice_candidate_content.name,
                management_api_client=management_api_client,
            )
        case _:
            raise RuntimeError(f"Unknown action: {payload.action}")

    return {}
