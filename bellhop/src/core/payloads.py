import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class ActionType(StrEnum):
    START_LOBBY = "start_lobby"
    JOIN_LOBBY = "join_lobby"
    ACCEPT_JOIN_REQUEST = "accept_join_request"
    REJECT_JOIN_REQUEST = "reject_join_request"
    SEND_SESSION_DESCRIPTION = "send_session_description"
    SEND_ICE_CANDIDATE = "send_ice_candidate"


class EventType(StrEnum):
    LOBBY_STARTED = "lobby_started"
    RECEIVED_JOIN_REQUEST = "received_join_request"
    JOIN_REQUEST_ACCEPTED = "join_request_accepted"
    JOIN_REQUEST_REJECTED = "join_request_rejected"
    RECEIVED_SESSION_DESCRIPTION = "received_session_description"
    RECEIVED_ICE_CANDIDATE = "received_ice_candidate"


@dataclass
class WebsocketPayload:
    action: ActionType
    content: Optional[dict] = None


@dataclass
class JoinLobbyContent:
    lobby_id: str


@dataclass
class AcceptJoinRequestContent:
    player_connection_id: str
    player_peer_id: int


@dataclass
class RejectJoinRequestContent:
    player_connection_id: str
    reason: str


@dataclass
class SendSessionDescriptionContent:
    connection_id: str
    session_type: str
    sdp: str


@dataclass
class SendICECandidateContent:
    connection_id: str
    media: str
    index: int
    name: str


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


def generate_join_request_accepted_event(host_connection_id: str, peer_id: int) -> str:
    return json.dumps(
        {
            "event": EventType.JOIN_REQUEST_ACCEPTED,
            "content": {"host_connection_id": host_connection_id, "peer_id": peer_id},
        }
    )


def generate_join_request_rejected_event(host_connection_id: str, reason: str) -> str:
    return json.dumps(
        {
            "event": EventType.JOIN_REQUEST_REJECTED,
            "content": {"host_connection_id": host_connection_id, "reason": reason},
        }
    )


def generate_received_session_description_event(
    connection_id: str, session_type: str, sdp: str
) -> str:
    return json.dumps(
        {
            "event": EventType.RECEIVED_SESSION_DESCRIPTION,
            "content": {
                "connection_id": connection_id,
                "session_type": session_type,
                "sdp": sdp,
            },
        }
    )


def generate_received_ice_candidate_event(
    connection_id: str,
    media: str,
    index: int,
    name: str,
) -> str:
    return json.dumps(
        {
            "event": EventType.RECEIVED_ICE_CANDIDATE,
            "content": {
                "connection_id": connection_id,
                "media": media,
                "index": index,
                "name": name,
            },
        }
    )
