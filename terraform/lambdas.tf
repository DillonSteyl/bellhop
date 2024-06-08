data "aws_iam_policy_document" "websocket_assume_role" {
  statement {
    sid    = "AllowLambdaAssumeRole"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "dynamodb_policy_doc" {
  statement {
    sid    = "AllowDynamoDBAccess"
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:UpdateItem",
    ]
    resources = [aws_dynamodb_table.websocket_connections.arn]
  }
}

resource "aws_iam_policy" "websocket_dynamodb_policy" {
  name        = "WebsocketDynamoDBPolicy"
  description = "Policy to allow Lambda to interact with DynamoDB"
  policy      = data.aws_iam_policy_document.dynamodb_policy_doc.json
}

resource "aws_iam_role" "lambda_iam_role" {
  name               = "WebsocketLambdaIAM"
  assume_role_policy = data.aws_iam_policy_document.websocket_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_execution_role" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "dynamodbo_policy_attachment" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = aws_iam_policy.websocket_dynamodb_policy.arn
}

resource "aws_iam_role_policy_attachment" "api_invoke" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonAPIGatewayInvokeFullAccess"
}

data "archive_file" "lambda_archive" {
  type        = "zip"
  output_path = "lambda.zip"
  source_dir  = "../bellhop/src"
  excludes    = ["tests"]
}

module "on_connect_lambda" {
  source                = "./modules/websocket_lambda"
  handler_function_name = "on_connect"
  lambda_name           = "websocket-on-connect"
  lambda_layers         = ["arn:aws:lambda:${local.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:71"]
  archive_folder        = data.archive_file.lambda_archive
  iam_role_arn          = aws_iam_role.lambda_iam_role.arn
  execution_arn         = aws_apigatewayv2_api.websocket_api.execution_arn
  dynamodb_table_name   = aws_dynamodb_table.websocket_connections.name
}

module "on_disconnect_lambda" {
  source                = "./modules/websocket_lambda"
  handler_function_name = "on_disconnect"
  lambda_name           = "websocket-on-disconnect"
  lambda_layers         = ["arn:aws:lambda:${local.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:71"]
  archive_folder        = data.archive_file.lambda_archive
  iam_role_arn          = aws_iam_role.lambda_iam_role.arn
  execution_arn         = aws_apigatewayv2_api.websocket_api.execution_arn
  dynamodb_table_name   = aws_dynamodb_table.websocket_connections.name
}

module "handle_payload_lambda" {
  source                = "./modules/websocket_lambda"
  handler_function_name = "handle_payload"
  lambda_name           = "websocket-handle-payload"
  lambda_layers         = ["arn:aws:lambda:${local.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:71"]
  archive_folder        = data.archive_file.lambda_archive
  iam_role_arn          = aws_iam_role.lambda_iam_role.arn
  execution_arn         = aws_apigatewayv2_api.websocket_api.execution_arn
  dynamodb_table_name   = aws_dynamodb_table.websocket_connections.name
}
