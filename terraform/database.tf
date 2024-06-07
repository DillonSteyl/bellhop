resource "aws_dynamodb_table" "websocket_connections" {
  name = "WebsocketConnections"
  attribute {
    name = "connectionId"
    type = "S"
  }
  hash_key     = "connectionId"
  billing_mode = "PAY_PER_REQUEST"
}
