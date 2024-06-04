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

data "archive_file" "on_connect_archive" {
  type        = "zip"
  source_file = "${path.module}/src/on_connect.py"
  output_path = "on_connect_lambda.zip"
}

resource "aws_lambda_function" "on_connect_lambda" {
  filename      = data.archive_file.on_connect_archive.output_path
  function_name = "websocket-on-connect"
  role          = aws_iam_role.lambda_iam_role.arn

  source_code_hash = data.archive_file.on_connect_archive.output_base64sha256

  runtime = "python3.12"
  handler = "on_connect.lambda_handler"

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.websocket_connections.name
    }
  }
}

resource "aws_lambda_permission" "allow_on_connect_api" {
  statement_id  = "AllowWebsocketInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.on_connect_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /* part allows invocation from any stage, method and resource path
  # within API Gateway.
  source_arn = "${aws_apigatewayv2_api.websocket_api.execution_arn}/*"
}

data "archive_file" "on_disconnect_archive" {
  type        = "zip"
  source_file = "${path.module}/src/on_disconnect.py"
  output_path = "on_disconnect_lambda.zip"
}

resource "aws_lambda_function" "on_disconnect_lambda" {
  filename      = data.archive_file.on_disconnect_archive.output_path
  function_name = "websocket-on-disconnect"
  role          = aws_iam_role.lambda_iam_role.arn

  source_code_hash = data.archive_file.on_disconnect_archive.output_base64sha256

  runtime = "python3.12"
  handler = "on_disconnect.lambda_handler"

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.websocket_connections.name
    }
  }
}

resource "aws_lambda_permission" "allow_on_disconnect_api" {
  statement_id  = "AllowWebsocketInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.on_disconnect_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /* part allows invocation from any stage, method and resource path
  # within API Gateway.
  source_arn = "${aws_apigatewayv2_api.websocket_api.execution_arn}/*"
}
