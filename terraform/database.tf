resource "aws_dynamodb_table" "websocket_connections" {
  name = "WebsocketConnections"

  attribute {
    name = "connectionId"
    type = "S"
  }

  attribute {
    name = "lobbyId"
    type = "S"
  }

  hash_key     = "connectionId"
  billing_mode = "PAY_PER_REQUEST"

  global_secondary_index {
    name            = "lobbyIndex"
    hash_key        = "lobbyId"
    projection_type = "ALL"
  }
}
