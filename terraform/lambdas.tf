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

resource "aws_iam_role_policy_attachment" "terraform_lambda_policy" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "dynamodbo_policy_attachment" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = aws_iam_policy.websocket_dynamodb_policy.arn
}

data "archive_file" "lambda_archive" {
  type        = "zip"
  output_path = "lambda.zip"
  source_dir  = "../bellhop/src"
}

module "on_connect_lambda" {
  source                = "./modules/websocket_lambda"
  handler_function_name = "on_connect"
  lambda_name           = "websocket-on-connect"
  archive_folder        = data.archive_file.lambda_archive
  iam_role_arn          = aws_iam_role.lambda_iam_role.arn
  execution_arn         = aws_apigatewayv2_api.websocket_api.execution_arn
  dynamodb_table_name   = aws_dynamodb_table.websocket_connections.name
}

module "on_disconnect_lambda" {
  source                = "./modules/websocket_lambda"
  handler_function_name = "on_disconnect"
  lambda_name           = "websocket-on-disconnect"
  archive_folder        = data.archive_file.lambda_archive
  iam_role_arn          = aws_iam_role.lambda_iam_role.arn
  execution_arn         = aws_apigatewayv2_api.websocket_api.execution_arn
  dynamodb_table_name   = aws_dynamodb_table.websocket_connections.name
}
