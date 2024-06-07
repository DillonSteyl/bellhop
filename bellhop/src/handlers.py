from utils import connections


def on_connect(event, context):
    """
    Handles new connections - inserting a row into DynamoDB
    """
    connection_id = event["requestContext"]["connectionId"]
    connections.add_connection(connection_id)
    return {}


def on_disconnect(event, context):
    """
    Handles disconnections - deleting a row from DynamoDB
    """
    connection_id = event["requestContext"]["connectionId"]
    connections.remove_connection(connection_id)
    return {}
