from .db import get_db, TABLE_NAME


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
