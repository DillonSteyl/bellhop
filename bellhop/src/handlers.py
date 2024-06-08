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
    actions.add_connection(event.request_context.connection_id)
    return {}


@event_source(data_class=APIGatewayProxyEvent)
def on_disconnect(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Handles disconnections - deleting a row from DynamoDB
    """
    actions.remove_connection(event.request_context.connection_id)
    return {}


@event_source(data_class=APIGatewayProxyEvent)
def handle_payload(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Generic handler for websocket requests
    """
    connection_id = event.request_context.connection_id
    payload = payloads.WebsocketPayload(**event.json_body)

    match payload.action:
        case payloads.ActionType.START_LOBBY:
            actions.start_lobby(
                connection_id,
                services.get_management_api_client(),
            )
        case _:
            raise RuntimeError(f"Unknown action: {payload.action}")

    return {}
