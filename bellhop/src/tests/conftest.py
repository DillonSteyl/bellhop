from unittest.mock import MagicMock

import pytest
from core.services import get_db, get_management_api_client
from mypy_boto3_dynamodb import DynamoDBClient
from typing import Generator

from .utils import clear_db


@pytest.fixture
def dynamo_client() -> Generator[DynamoDBClient, None, None]:
    """
    Dynamo client fixture that clears out the database before & after each test.
    """
    db = get_db()
    clear_db(db)
    yield db
    clear_db(db)


@pytest.fixture
def management_api_client() -> MagicMock:
    """
    API Gateway Management API fixture
    """
    return get_management_api_client()
