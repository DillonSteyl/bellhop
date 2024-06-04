resource "aws_dynamodb_table" "websocket_connections" {
  name = "WebsocketConnections"
  attribute {
    name = "connectionId"
    type = "S"
  }
  hash_key       = "connectionId"
  read_capacity  = 10
  write_capacity = 10
}
