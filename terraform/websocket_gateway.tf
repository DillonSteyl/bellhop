
// Websocket API
resource "aws_apigatewayv2_api" "websocket_api" {
  name                       = "websocket-signalling-api"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"
}

// Stages
resource "aws_apigatewayv2_stage" "websocket_prod_stage" {
  api_id      = aws_apigatewayv2_api.websocket_api.id
  name        = "production"
  auto_deploy = true

  default_route_settings {
    logging_level          = "INFO"
    throttling_rate_limit  = 100
    throttling_burst_limit = 10
  }
}

// Integrations
resource "aws_apigatewayv2_integration" "connect_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"

  connection_type           = "INTERNET"
  content_handling_strategy = "CONVERT_TO_TEXT"
  integration_uri           = module.on_connect_lambda.invoke_arn
  integration_method        = "POST"
}

resource "aws_apigatewayv2_integration" "disconnect_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"

  connection_type           = "INTERNET"
  content_handling_strategy = "CONVERT_TO_TEXT"
  integration_uri           = module.on_disconnect_lambda.invoke_arn
  integration_method        = "POST"
}

resource "aws_apigatewayv2_integration" "default_integration" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "AWS_PROXY"

  connection_type           = "INTERNET"
  content_handling_strategy = "CONVERT_TO_TEXT"
  integration_uri           = module.handle_payload_lambda.invoke_arn
  integration_method        = "POST"
}

// Routes
resource "aws_apigatewayv2_route" "connect_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "$connect"
  target    = "integrations/${aws_apigatewayv2_integration.connect_integration.id}"
}

resource "aws_apigatewayv2_route" "disconnect_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.disconnect_integration.id}"
}

resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.default_integration.id}"
}
