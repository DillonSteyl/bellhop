resource "aws_lambda_function" "lambda" {
  filename      = var.archive_folder.output_path
  function_name = var.lambda_name
  role          = var.iam_role_arn

  source_code_hash = var.archive_folder.output_base64sha256

  runtime = "python3.12"
  handler = "${var.handler_filename}.${var.handler_function_name}"

  environment {
    variables = {
      TABLE_NAME           = var.dynamodb_table_name
      DEPLOYED_ENVIRONMENT = var.deployed_environment
    }
  }
}

resource "aws_lambda_permission" "allow_apigateway_invoke" {
  statement_id  = "AllowWebsocketInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /* part allows invocation from any stage, method and resource path
  # within API Gateway.
  source_arn = "${var.execution_arn}/*"
}
