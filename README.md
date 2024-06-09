<p align="center">
  <img src="docs/bellhop_title_transparent.png" width="600">
</p>

**Bellhop** is a serverless WebSocket API for managing P2P game lobbies - it acts as a WebRTC signalling server, allowing players to exchange SDP messages and ICE candidates to establish direct connections with one another.

### Contents

- [Architecture & Deployment](#architecture--deployment)
- [Local Development & Testing](#local-development--testing)
- [Implementation](#implementation)

## Architecture & Deployment

Bellhop's infrastructure is managed using Terraform and deployed to AWS.

![Architecture Overview](docs/architecture.png)

- **Websocket API Gateway** provides the API and integrations with AWS Lambda.
- **AWS Lambda** handles the core logic.
- **DynamoDB** is used to store the currently open connections and lobbies.

## Local Development & Testing

A [localstack](https://www.localstack.cloud) container is used to emulate portions of the stack for testing and local development.

- `docker compose up localstack-setup` will spin up the `localstack` and `localstack-setup` containers. The `setup` container uses the [tflocal wrapper script](https://docs.localstack.cloud/user-guide/integrations/terraform/#tflocal-wrapper-script) to spin up a subset of the AWS services which can be tested against.
- `docker compose run bellhop bash` will shell into a container containing the `bellhop` source code. You can then open a python terminal and run code against the local `dynamodb` instance, for example:
  ```py
  >>> from core import services, actions
  >>> from tests import utils
  >>> dynamo = services.get_db()
  >>> dynamo.list_tables()["TableNames"]
  ['WebsocketConnections']
  >>> actions.add_connection("some-connection-id")
  >>> utils.get_all_dynamo_items(dynamo)
  [{'connectionId': {'S': 'some-connection-id'}}]
  ```
- `docker compose run bellhop pytest` will run the automated tests against the localstack.

## Implementation

The following section describes the basic principles behind Bellhop's implementation and how it can be used in practice.

### Actions & Events

Bellhop messages can be partitioned into _actions_ and _events_:

- **Actions** are requests from a client to Bellhop to do something("start a lobby", "request to join a lobby", etc).
  ```json
  {
    "action": "name_of_action",
    "content": {
      // depends on the action
      "key": "value",
    }
  }
  ```
- **Events** are bellhop's response to an action (e.g. "lobby started").
  ```json
  {
    "event": "name_of_event",
    "content": {
      // depends on the action
      "key": "value",
    }
  }
  ```

### Starting a Lobby

Starting a lobby is a simple process, consisting of only one action.

```mermaid
sequenceDiagram
    Host->>Bellhop: ACTION: start_lobby
    Bellhop->>Host: EVENT: lobby_started (lobby_id)
```

### Joining a Lobby

Joining a lobby is much more complicated, because it involves exchanging messages and candidates in order to bypass the signalling server and establish a direct WebRTC connection between two peers.

```mermaid
sequenceDiagram
    participant Client
    participant Bellhop
    # participant DynamoDB
    participant Host
    Client->>Bellhop: ACTION: join_lobby (lobby_id)
    # Bellhop-->DynamoDB: Query for host of lobby
    Bellhop->>Host: EVENT: 'request_to_join' (connection_id)
    Host-->>Host: Decide whether to accept/reject
    break if request is rejected
        Host-->>Bellhop: ACTION: 'reject_join_request' (connection_id)
        Bellhop--)Client: EVENT: 'request_rejected'
    end
    Host->>Bellhop: ACTION: 'accept_request'
    Bellhop-)Client: EVENT: 'request_accepted' (host_connection_id)
    Host->>Host: Create WebRTC offer
    activate Host
    Note right of Host: Generate SDP and ICE candidates
    Host->>Bellhop: ACTION: 'set_session_description' (connection_id)
    Bellhop-)Client: EVENT: 'received_session_description'
    Client->>Client: Set remote session description
    
    loop foreach ICE candidate generated
        Host->>Bellhop: ACTION: 'send_ice_candidate' (connection_id)
        Bellhop-)Client: EVENT: 'received_ice_candidate'
        Client->>Client: Add ICE Candidate
    end
    deactivate Host
    activate Client
    Note left of Client: Generate SDP and ICE candidates
    Client-)Bellhop: ACTION: 'set_session_description' (connection_id)
    Bellhop-)Host: EVENT: 'received_session_description'
    Host->>Host: Set remote session description

    loop foreach ICE candidate generated
        Client->>Bellhop: ACTION: 'send_ice_candidate' (connection_id)
        Bellhop-)Host: EVENT: 'received_ice_candidate'
        Host->>Host: Add ICE Candidate
    end
    deactivate Client

    Client-->Host: WebRTC algorithm establishes connection
```
