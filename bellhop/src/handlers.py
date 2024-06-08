from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)
from aws_lambda_powertools.utilities.typing import LambdaContext
from utils import connections


@event_source(data_class=APIGatewayProxyEvent)
def on_connect(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Handles new connections - inserting a row into DynamoDB
    """
    connections.add_connection(event.request_context.connection_id)
    return {}


@event_source(data_class=APIGatewayProxyEvent)
def on_disconnect(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Handles disconnections - deleting a row from DynamoDB
    """
    connections.remove_connection(event.request_context.connection_id)
    return {}


@event_source(data_class=APIGatewayProxyEvent)
def handle_payload(event: APIGatewayProxyEvent, context: LambdaContext):
    """
    Generic handler for websocket requests
    """
    print(event)
    print(context)
    return {}
