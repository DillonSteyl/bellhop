import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class ActionType(StrEnum):
    START_LOBBY = "start_lobby"


class EventType(StrEnum):
    LOBBY_STARTED = "lobby_started"


@dataclass
class WebsocketPayload:
    action: ActionType
    content: Optional[dict] = None


def generate_lobby_started_event(lobby_id: str) -> str:
    return json.dumps(
        {
            "event": EventType.LOBBY_STARTED,
            "content": {"lobbyId": lobby_id},
        }
    )
