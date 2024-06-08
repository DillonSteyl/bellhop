import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class ActionType(StrEnum):
    START_LOBBY = "start_lobby"
    JOIN_LOBBY = "join_lobby"


class EventType(StrEnum):
    LOBBY_STARTED = "lobby_started"
    RECEIVED_JOIN_REQUEST = "received_join_request"


@dataclass
class WebsocketPayload:
    action: ActionType
    content: Optional[dict] = None


@dataclass
class JoinLobbyContent:
    lobby_id: str


def generate_lobby_started_event(lobby_id: str) -> str:
    return json.dumps(
        {
            "event": EventType.LOBBY_STARTED,
            "content": {"lobby_id": lobby_id},
        }
    )


def generate_received_join_request_event(requesting_player_connection_id: str) -> str:
    return json.dumps(
        {
            "event": EventType.RECEIVED_JOIN_REQUEST,
            "content": {"connection_id": requesting_player_connection_id},
        }
    )
