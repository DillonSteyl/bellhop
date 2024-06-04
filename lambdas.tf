data "aws_iam_policy_document" "websocket_lambda_policy" {
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

resource "aws_iam_role" "lambda_iam_role" {
  name               = "WebsocketLambdaIAM"
  assume_role_policy = data.aws_iam_policy_document.websocket_lambda_policy.json
}

resource "aws_iam_role_policy_attachment" "terraform_lambda_policy" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "archive_file" "on_connect_archive" {
  type        = "zip"
  source_file = "${path.module}/src/on_connect.py"
  output_path = "on_connect_lambda.zip"
}

resource "aws_lambda_function" "on_connect_lambda" {
  filename      = "on_connect_lambda.zip"
  function_name = "websocket-on-connect"
  role          = aws_iam_role.lambda_iam_role.arn

  source_code_hash = data.archive_file.on_connect_archive.output_base64sha256

  runtime = "python3.12"
  handler = "on_connect.lambda_handler"
}

resource "aws_lambda_permission" "allow_api" {
  statement_id  = "AllowWebsocketInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.on_connect_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /* part allows invocation from any stage, method and resource path
  # within API Gateway.
  source_arn = "${aws_apigatewayv2_api.websocket_api.execution_arn}/*"
}
